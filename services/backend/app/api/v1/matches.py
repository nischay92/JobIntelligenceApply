from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.repositories.jobs import JobRepository
from app.repositories.matches import JobMatchRepository
from app.repositories.resumes import ResumeRepository
from app.schemas.matches import JobMatchResponse, ScoreJobsRequest, ScoreJobsResponse
from app.services.match_scoring import score_resume_against_job

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=list[JobMatchResponse])
def list_matches(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[JobMatchResponse]:
    return [JobMatchResponse.model_validate(match) for match in JobMatchRepository(db).list_for_user(user.id, limit=limit)]


@router.get("/{match_id}", response_model=JobMatchResponse)
def get_match(
    match_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> JobMatchResponse:
    match = JobMatchRepository(db).get_for_user(user_id=user.id, match_id=match_id)
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")
    return JobMatchResponse.model_validate(match)


@router.post("/score", response_model=ScoreJobsResponse)
def score_jobs(
    request: ScoreJobsRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ScoreJobsResponse:
    resume_repository = ResumeRepository(db)
    resume = (
        resume_repository.get_for_user(user_id=user.id, resume_id=request.resume_id)
        if request.resume_id
        else resume_repository.get_active_parsed_for_user(user.id)
    )
    if resume is None or resume.status != "parsed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A parsed resume is required.")

    job_repository = JobRepository(db)
    jobs = [job_repository.get_by_id(job_id) for job_id in request.job_ids] if request.job_ids else job_repository.list_jobs(limit=100)
    jobs = [job for job in jobs if job is not None]
    match_repository = JobMatchRepository(db)
    for job in jobs:
        score = score_resume_against_job(resume=resume, job=job)
        match_repository.upsert(user_id=user.id, resume_id=resume.id, job_id=job.id, score=score)

    return ScoreJobsResponse(status="scored", scored_count=len(jobs))
