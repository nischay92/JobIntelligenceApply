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
