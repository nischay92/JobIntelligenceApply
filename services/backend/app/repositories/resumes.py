from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Resume


class ResumeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: str,
        original_filename: str,
        file_mime_type: str,
        file_size_bytes: int,
        storage_path: str,
        active: bool,
    ) -> Resume:
        resume = Resume(
            user_id=user_id,
            original_filename=original_filename,
            file_mime_type=file_mime_type,
            file_size_bytes=file_size_bytes,
            storage_path=storage_path,
            status="uploaded",
            active=active,
        )
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def list_for_user(self, user_id: str) -> list[Resume]:
        return list(
            self.db.scalars(
                select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
            )
        )

    def has_any_for_user(self, user_id: str) -> bool:
        return self.db.scalar(select(Resume.id).where(Resume.user_id == user_id).limit(1)) is not None

    def get_for_user(self, *, user_id: str, resume_id: str) -> Resume | None:
        return self.db.scalar(select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id))

    def mark_parsing(self, resume: Resume) -> Resume:
        resume.status = "parsing"
        resume.parse_error = None
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def mark_parsed(
        self,
        resume: Resume,
        *,
        parsed_profile: dict,
        plain_text: str,
        vector_id: str,
        parser_version: str,
    ) -> Resume:
        resume.status = "parsed"
        resume.parsed_profile = parsed_profile
        resume.plain_text = plain_text
        resume.vector_id = vector_id
        resume.parser_version = parser_version
        resume.parse_error = None
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def mark_failed(self, resume: Resume, *, error: str) -> Resume:
        resume.status = "failed"
        resume.parse_error = error
        self.db.commit()
        self.db.refresh(resume)
        return resume
