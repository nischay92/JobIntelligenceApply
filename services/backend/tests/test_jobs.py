from fastapi.testclient import TestClient

from app.db.models import Job, ProcessingRun


def test_jobs_require_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/jobs")

    assert response.status_code == 401


def test_sample_discovery_creates_job(authenticated_client: TestClient, db_session) -> None:
    response = authenticated_client.post(
        "/api/v1/jobs/discovery-runs",
        json={"source": "sample", "company": "Demo Co", "limit": 5},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "succeeded"
    assert payload["records_seen"] == 1
    assert payload["records_created"] == 1
    assert db_session.query(Job).count() == 1
    assert db_session.query(ProcessingRun).count() == 1

    list_response = authenticated_client.get("/api/v1/jobs")
    assert list_response.status_code == 200
    assert list_response.json()[0]["company"] == "Demo Co"
    assert list_response.json()[0]["title"] == "Backend Engineer"


def test_discovery_upserts_duplicate_jobs(authenticated_client: TestClient) -> None:
    for _ in range(2):
        response = authenticated_client.post(
            "/api/v1/jobs/discovery-runs",
            json={"source": "sample", "company": "Demo Co", "limit": 5},
        )
        assert response.status_code == 201

    response = authenticated_client.get("/api/v1/jobs")

    assert len(response.json()) == 1


def test_discovery_requires_board_token_for_public_board(authenticated_client: TestClient) -> None:
    response = authenticated_client.post(
        "/api/v1/jobs/discovery-runs",
        json={"source": "greenhouse", "limit": 5},
    )

    assert response.status_code == 400


def test_internal_discovery_does_not_require_user_session(client: TestClient, db_session) -> None:
    response = client.post(
        "/internal/v1/jobs/discovery-runs",
        json={"source": "sample", "company": "Scheduler Demo", "limit": 5},
    )

    assert response.status_code == 201
    assert response.json()["records_created"] == 1
