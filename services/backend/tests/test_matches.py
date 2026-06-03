from fastapi.testclient import TestClient


def _upload_parsed_resume(authenticated_client: TestClient, monkeypatch) -> str:
    upload_response = authenticated_client.post(
        "/api/v1/resumes",
        files={"file": ("resume.pdf", b"%PDF-1.4", "application/pdf")},
    )
    resume_id = upload_response.json()["id"]

    async def fake_parse_resume(_resume):
        return {
            "profile": {
                "skills": ["Python", "FastAPI", "PostgreSQL", "React"],
                "experience": ["Built APIs and job matching systems"],
                "projects": ["ApplyWise AI"],
                "education": ["B.S. Computer Science"],
                "certifications": [],
                "keywords": ["Python", "FastAPI", "PostgreSQL", "React", "APIs"],
            },
            "plain_text": "Skills Python FastAPI PostgreSQL React",
            "embedding": [0.1, 0.2],
            "parser_version": "test-parser",
            "vector_id": f"resume-{resume_id}-vector",
        }

    monkeypatch.setattr("app.api.v1.resumes.parse_resume_with_ai_service", fake_parse_resume)
    parse_response = authenticated_client.post(f"/api/v1/resumes/{resume_id}/parse")
    assert parse_response.status_code == 200
    return resume_id


def _discover_sample_job(authenticated_client: TestClient) -> str:
    response = authenticated_client.post(
        "/api/v1/jobs/discovery-runs",
        json={"source": "sample", "company": "Demo Co", "limit": 5},
    )
    assert response.status_code == 201
    jobs_response = authenticated_client.get("/api/v1/jobs")
    return jobs_response.json()[0]["id"]


def test_score_jobs_requires_parsed_resume(authenticated_client: TestClient) -> None:
    _discover_sample_job(authenticated_client)

    response = authenticated_client.post("/api/v1/matches/score", json={"job_ids": []})

    assert response.status_code == 400


def test_score_jobs_creates_match(authenticated_client: TestClient, monkeypatch) -> None:
    _upload_parsed_resume(authenticated_client, monkeypatch)
    job_id = _discover_sample_job(authenticated_client)

    response = authenticated_client.post("/api/v1/matches/score", json={"job_ids": [job_id]})

    assert response.status_code == 200
    assert response.json()["scored_count"] == 1

    matches_response = authenticated_client.get("/api/v1/matches")
    assert matches_response.status_code == 200
    match = matches_response.json()[0]
    assert match["overall_score"] >= 70
    assert match["skill_score"] >= 50
    assert match["priority"] in {"high", "medium", "low"}
    assert match["job"]["id"] == job_id


def test_score_jobs_upserts_existing_match(authenticated_client: TestClient, monkeypatch) -> None:
    _upload_parsed_resume(authenticated_client, monkeypatch)
    job_id = _discover_sample_job(authenticated_client)

    for _ in range(2):
        response = authenticated_client.post("/api/v1/matches/score", json={"job_ids": [job_id]})
        assert response.status_code == 200

    matches_response = authenticated_client.get("/api/v1/matches")

    assert len(matches_response.json()) == 1
