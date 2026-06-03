from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from app.core.config import settings
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


def test_user_repository_upserts_google_user(db_session) -> None:
    repository = UserRepository(db_session)
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
    assert db_session.query(User).count() == 1


def test_me_returns_authenticated_user(authenticated_client: TestClient) -> None:
    response = authenticated_client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "person@example.com"
