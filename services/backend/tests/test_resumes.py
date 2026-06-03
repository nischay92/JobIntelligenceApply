from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.models import Resume


def test_resume_upload_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/v1/resumes",
        files={"file": ("resume.pdf", b"%PDF-1.4", "application/pdf")},
    )

    assert response.status_code == 401


def test_resume_upload_accepts_pdf(
    authenticated_client: TestClient,
    db_session,
    upload_dir: Path,
) -> None:
    response = authenticated_client.post(
        "/api/v1/resumes",
        files={"file": ("resume.pdf", b"%PDF-1.4\ncontent", "application/pdf")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["original_filename"] == "resume.pdf"
    assert payload["file_mime_type"] == "application/pdf"
    assert payload["file_size_bytes"] == len(b"%PDF-1.4\ncontent")
    assert payload["status"] == "uploaded"
    assert payload["active"] is True

    resume = db_session.query(Resume).one()
    assert Path(resume.storage_path).exists()
    assert upload_dir in Path(resume.storage_path).parents


def test_resume_upload_accepts_docx(authenticated_client: TestClient) -> None:
    response = authenticated_client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "resume.docx",
                b"PK\x03\x04docx-content",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["original_filename"] == "resume.docx"


def test_resume_upload_rejects_unsupported_mime(authenticated_client: TestClient) -> None:
    response = authenticated_client.post(
        "/api/v1/resumes",
        files={"file": ("resume.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 415


def test_resume_upload_rejects_extension_mismatch(authenticated_client: TestClient) -> None:
    response = authenticated_client.post(
        "/api/v1/resumes",
        files={"file": ("resume.txt", b"%PDF-1.4", "application/pdf")},
    )

    assert response.status_code == 400


def test_resume_upload_rejects_large_files(
    authenticated_client: TestClient,
    monkeypatch,
    upload_dir: Path,
) -> None:
    monkeypatch.setattr(settings, "max_upload_size_bytes", 4)

    response = authenticated_client.post(
        "/api/v1/resumes",
        files={"file": ("resume.pdf", b"12345", "application/pdf")},
    )

    assert response.status_code == 413
    assert list(upload_dir.rglob("*")) == []


def test_resume_list_returns_user_resumes(authenticated_client: TestClient) -> None:
    authenticated_client.post(
        "/api/v1/resumes",
        files={"file": ("resume.pdf", b"%PDF-1.4", "application/pdf")},
    )

    response = authenticated_client.get("/api/v1/resumes")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["original_filename"] == "resume.pdf"
