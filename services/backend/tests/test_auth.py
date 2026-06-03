from collections.abc import Generator
from base64 import b64encode
import json
from urllib.parse import parse_qs, urlparse

from itsdangerous import TimestampSigner
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.auth import get_db
from app.core.config import settings
from app.db.base import Base
from app.db.models import User
from app.main import app
from app.repositories.users import UserRepository


def test_google_login_returns_authorization_url(monkeypatch) -> None:
    monkeypatch.setattr(settings, "google_client_id", "client-id")
    monkeypatch.setattr(settings, "google_client_secret", "client-secret")

    response = TestClient(app).get("/api/v1/auth/google/login")

    assert response.status_code == 200
    authorization_url = response.json()["authorization_url"]
    parsed = urlparse(authorization_url)
    query = parse_qs(parsed.query)
    assert parsed.netloc == "accounts.google.com"
    assert query["client_id"] == ["client-id"]
    assert query["scope"] == ["openid email profile"]
    assert query["redirect_uri"] == [settings.google_redirect_uri]
    assert query["state"][0]


def test_google_login_requires_oauth_configuration(monkeypatch) -> None:
    monkeypatch.setattr(settings, "google_client_id", "")
    monkeypatch.setattr(settings, "google_client_secret", "")

    response = TestClient(app).get("/api/v1/auth/google/login")

    assert response.status_code == 503


def test_me_requires_authenticated_session() -> None:
    response = TestClient(app).get("/api/v1/auth/me")

    assert response.status_code == 401


def test_user_repository_upserts_google_user() -> None:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)

    with session_factory() as session:
        repository = UserRepository(session)
        created = repository.upsert_google_user(
            google_sub="google-sub",
            email="first@example.com",
            name="First User",
            avatar_url=None,
        )
        updated = repository.upsert_google_user(
            google_sub="google-sub",
            email="updated@example.com",
            name="Updated User",
            avatar_url="https://example.com/avatar.png",
        )

        assert created.id == updated.id
        assert updated.email == "updated@example.com"
        assert updated.name == "Updated User"
        assert session.query(User).count() == 1


def test_me_returns_authenticated_user() -> None:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)

    with session_factory() as seed_session:
        user = User(
            google_sub="google-sub",
            email="person@example.com",
            name="Person Example",
            avatar_url=None,
        )
        seed_session.add(user)
        seed_session.commit()
        seed_session.refresh(user)
        user_id = user.id

    def override_get_db() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    session_cookie = TimestampSigner(settings.session_secret).sign(
        b64encode(json.dumps({"user_id": user_id}).encode("utf-8"))
    )
    client.cookies.set(settings.session_cookie_name, session_cookie.decode("utf-8"))

    try:
        response = client.get("/api/v1/auth/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["email"] == "person@example.com"
