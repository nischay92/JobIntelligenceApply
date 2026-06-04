from fastapi.testclient import TestClient


def _setup_scored_job(authenticated_client: TestClient, monkeypatch) -> tuple[str, str]:
    upload_response = authenticated_client.post(
        "/api/v1/resumes",
        files={"file": ("resume.pdf", b"%PDF-1.4", "application/pdf")},
    )
    resume_id = upload_response.json()["id"]

    async def fake_parse_resume(_resume):
        return {
            "profile": {
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "experience": ["Built APIs for job platforms"],
                "projects": ["ApplyWise AI"],
                "education": ["B.S. Computer Science"],
                "certifications": [],
                "keywords": ["Python", "FastAPI", "PostgreSQL", "APIs"],
            },
            "plain_text": "Skills Python FastAPI PostgreSQL",
            "embedding": [0.1, 0.2],
            "parser_version": "test-parser",
            "vector_id": f"resume-{resume_id}-vector",
        }

    monkeypatch.setattr("app.api.v1.resumes.parse_resume_with_ai_service", fake_parse_resume)
    assert authenticated_client.post(f"/api/v1/resumes/{resume_id}/parse").status_code == 200

    assert (
        authenticated_client.post(
            "/api/v1/jobs/discovery-runs",
            json={"source": "sample", "company": "Demo Co", "limit": 5},
        ).status_code
        == 201
    )
    job_id = authenticated_client.get("/api/v1/jobs").json()[0]["id"]
    assert authenticated_client.post("/api/v1/matches/score", json={"job_ids": [job_id]}).status_code == 200
    return resume_id, job_id


def test_generate_cover_letter_draft(authenticated_client: TestClient, monkeypatch) -> None:
    resume_id, job_id = _setup_scored_job(authenticated_client, monkeypatch)

    response = authenticated_client.post(
        "/api/v1/generated-answers",
        json={"resume_id": resume_id, "job_id": job_id, "content_type": "cover_letter"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "draft"
    assert payload["content_type"] == "cover_letter"
    assert "Draft for human review" in payload["content"]
    assert "does not submit applications" in payload["content"]
    assert payload["extra_metadata"]["human_approval_required"] is True


def test_generated_answers_can_be_listed_and_reviewed(
    authenticated_client: TestClient,
    monkeypatch,
) -> None:
    resume_id, job_id = _setup_scored_job(authenticated_client, monkeypatch)
    created = authenticated_client.post(
        "/api/v1/generated-answers",
        json={"resume_id": resume_id, "job_id": job_id, "content_type": "recruiter_email"},
    ).json()

    list_response = authenticated_client.get("/api/v1/generated-answers")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = authenticated_client.patch(
        f"/api/v1/generated-answers/{created['id']}",
        json={"status": "approved", "content": "Reviewed draft content."},
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "approved"
    assert update_response.json()["content"] == "Reviewed draft content."


def test_generate_answer_requires_parsed_resume(authenticated_client: TestClient) -> None:
    job_response = authenticated_client.post(
        "/api/v1/jobs/discovery-runs",
        json={"source": "sample", "company": "Demo Co", "limit": 5},
    )
    assert job_response.status_code == 201
    job_id = authenticated_client.get("/api/v1/jobs").json()[0]["id"]

    response = authenticated_client.post(
        "/api/v1/generated-answers",
        json={"job_id": job_id, "content_type": "why_fit"},
    )

    assert response.status_code == 400
