from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.repositories.resumes import ResumeRepository
from app.schemas.resumes import ResumeResponse
from app.services.resume_parser_client import parse_resume_with_ai_service
from app.services.resume_storage import store_resume_upload

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeResponse, status_code=201)
async def upload_resume(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File()],
) -> ResumeResponse:
    repository = ResumeRepository(db)
    storage_path, original_filename, file_size = await store_resume_upload(
        user_id=user.id,
        upload=file,
    )
    resume = repository.create(
        user_id=user.id,
        original_filename=original_filename,
        file_mime_type=file.content_type or "application/octet-stream",
        file_size_bytes=file_size,
        storage_path=storage_path,
        active=not repository.has_any_for_user(user.id),
    )
    return ResumeResponse.model_validate(resume)


@router.get("", response_model=list[ResumeResponse])
def list_resumes(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[ResumeResponse]:
    return [ResumeResponse.model_validate(resume) for resume in ResumeRepository(db).list_for_user(user.id)]


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ResumeResponse:
    resume = ResumeRepository(db).get_for_user(user_id=user.id, resume_id=resume_id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    return ResumeResponse.model_validate(resume)


@router.post("/{resume_id}/parse", response_model=ResumeResponse)
async def parse_resume(
    resume_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ResumeResponse:
    repository = ResumeRepository(db)
    resume = repository.get_for_user(user_id=user.id, resume_id=resume_id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    repository.mark_parsing(resume)
    try:
        parsed = await parse_resume_with_ai_service(resume)
    except Exception as exc:
        repository.mark_failed(resume, error=str(exc))
        raise

    resume = repository.mark_parsed(
        resume,
        parsed_profile=parsed["profile"],
        plain_text=parsed["plain_text"],
        vector_id=parsed["vector_id"],
        parser_version=parsed["parser_version"],
    )
    return ResumeResponse.model_validate(resume)
