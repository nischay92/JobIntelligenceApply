from base64 import b64encode
from collections.abc import Generator
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.core.config import settings
from app.db.base import Base
from app.db.models import User
from app.main import app


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with session_factory() as session:
            yield session
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def authenticated_client(client: TestClient, db_session: Session) -> TestClient:
    user = User(
        google_sub="google-sub",
        email="person@example.com",
        name="Person Example",
        avatar_url=None,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    session_cookie = TimestampSigner(settings.session_secret).sign(
        b64encode(json.dumps({"user_id": user.id}).encode("utf-8"))
    )
    client.cookies.set(settings.session_cookie_name, session_cookie.decode("utf-8"))
    return client


@pytest.fixture(autouse=True)
def upload_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(settings, "upload_storage_dir", str(tmp_path))
    monkeypatch.setattr(settings, "max_upload_size_bytes", 5 * 1024 * 1024)
    return tmp_path
