from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.repositories.jobs import JobRepository
from app.schemas.jobs import JobDiscoveryRequest, JobDiscoveryResponse, JobResponse
from app.services.job_discovery import run_discovery

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobResponse])
def list_jobs(
    _user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    q: Annotated[str | None, Query(max_length=120)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[JobResponse]:
    return [JobResponse.model_validate(job) for job in JobRepository(db).list_jobs(query=q, limit=limit)]


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    _user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> JobResponse:
    job = JobRepository(db).get_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return JobResponse.model_validate(job)


@router.post("/discovery-runs", response_model=JobDiscoveryResponse, status_code=201)
async def create_discovery_run(
    request: JobDiscoveryRequest,
    _user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> JobDiscoveryResponse:
    return await run_discovery(db, request)
