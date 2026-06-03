from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models import JobMatch


class JobMatchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_user(self, user_id: str, *, limit: int = 50) -> list[JobMatch]:
        return list(
            self.db.scalars(
                select(JobMatch)
                .options(joinedload(JobMatch.job), joinedload(JobMatch.resume))
                .where(JobMatch.user_id == user_id)
                .order_by(JobMatch.overall_score.desc(), JobMatch.created_at.desc())
                .limit(limit)
            )
        )

    def get_for_user(self, *, user_id: str, match_id: str) -> JobMatch | None:
        return self.db.scalar(
            select(JobMatch)
            .options(joinedload(JobMatch.job), joinedload(JobMatch.resume))
            .where(JobMatch.user_id == user_id, JobMatch.id == match_id)
        )

    def upsert(self, *, user_id: str, resume_id: str, job_id: str, score: dict) -> JobMatch:
        match = self.db.scalar(
            select(JobMatch).where(
                JobMatch.user_id == user_id,
                JobMatch.resume_id == resume_id,
                JobMatch.job_id == job_id,
            )
        )
        if match is None:
            match = JobMatch(user_id=user_id, resume_id=resume_id, job_id=job_id, **score)
            self.db.add(match)
        else:
            for key, value in score.items():
                setattr(match, key, value)

        self.db.commit()
        self.db.refresh(match)
        return match
