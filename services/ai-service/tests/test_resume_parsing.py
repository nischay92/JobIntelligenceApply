from fastapi.testclient import TestClient

from app.main import app
from app.parsers.resumes import parse_resume_text
from app.vectorstore.embeddings import deterministic_embedding


def test_parse_resume_text_extracts_structured_profile() -> None:
    profile = parse_resume_text(
        """
        Skills
        Python, FastAPI, React, PostgreSQL
        Experience
        - Built APIs for job matching systems
        Projects
        - ApplyWise AI
        Education
        B.S. Computer Science
        Certifications
        AWS Certified Developer
        """
    )

    assert profile.skills == ["Python", "FastAPI", "React", "PostgreSQL"]
    assert "Built APIs for job matching systems" in profile.experience
    assert "ApplyWise AI" in profile.projects
    assert "B.S. Computer Science" in profile.education
    assert "AWS Certified Developer" in profile.certifications


def test_embedding_is_deterministic() -> None:
    first = deterministic_embedding("Python FastAPI React")
    second = deterministic_embedding("Python FastAPI React")

    assert first == second
    assert len(first) == 64


def test_parse_endpoint_rejects_unsupported_file() -> None:
    response = TestClient(app).post(
        "/api/v1/resumes/parse",
        files={"file": ("resume.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 415
