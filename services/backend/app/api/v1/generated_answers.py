from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.repositories.generated_answers import GeneratedAnswerRepository
from app.repositories.jobs import JobRepository
from app.repositories.matches import JobMatchRepository
from app.repositories.resumes import ResumeRepository
from app.schemas.generated_answers import (
    GenerateAnswerRequest,
    GeneratedAnswerResponse,
    UpdateGeneratedAnswerRequest,
)
from app.services.application_assistant import generate_application_content

router = APIRouter(prefix="/generated-answers", tags=["generated-answers"])


@router.get("", response_model=list[GeneratedAnswerResponse])
def list_generated_answers(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[GeneratedAnswerResponse]:
    answers = GeneratedAnswerRepository(db).list_for_user(user.id, limit=limit)
    return [GeneratedAnswerResponse.model_validate(answer) for answer in answers]


@router.post("", response_model=GeneratedAnswerResponse, status_code=201)
def generate_answer(
    request: GenerateAnswerRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> GeneratedAnswerResponse:
    resume_repository = ResumeRepository(db)
    resume = (
        resume_repository.get_for_user(user_id=user.id, resume_id=request.resume_id)
        if request.resume_id
        else resume_repository.get_active_parsed_for_user(user.id)
    )
    if resume is None or resume.status != "parsed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A parsed resume is required.")

    job = JobRepository(db).get_by_id(request.job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    match = None
    for candidate in JobMatchRepository(db).list_for_user(user.id, limit=100):
        if candidate.resume_id == resume.id and candidate.job_id == job.id:
            match = candidate
            break

    generated = generate_application_content(
        resume=resume,
        job=job,
        match=match,
        content_type=request.content_type,
        prompt_label=request.prompt_label,
    )
    answer = GeneratedAnswerRepository(db).create(
        user_id=user.id,
        resume_id=resume.id,
        job_id=job.id,
        content_type=request.content_type,
        prompt_label=request.prompt_label,
        content=generated["content"],
        metadata=generated["metadata"],
        vector_id=generated["vector_id"],
    )
    return GeneratedAnswerResponse.model_validate(answer)


@router.patch("/{answer_id}", response_model=GeneratedAnswerResponse)
def update_generated_answer(
    answer_id: str,
    request: UpdateGeneratedAnswerRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> GeneratedAnswerResponse:
    repository = GeneratedAnswerRepository(db)
    answer = repository.get_for_user(user_id=user.id, answer_id=answer_id)
    if answer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated answer not found.")

    answer = repository.update(answer, content=request.content, status=request.status)
    return GeneratedAnswerResponse.model_validate(answer)
