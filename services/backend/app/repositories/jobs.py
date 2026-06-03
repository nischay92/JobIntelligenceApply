from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models import Job, ProcessingRun


class JobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_jobs(self, *, query: str | None = None, limit: int = 50) -> list[Job]:
        statement = select(Job).order_by(Job.discovered_at.desc()).limit(limit)
        if query:
            like = f"%{query}%"
            statement = (
                select(Job)
                .where(or_(Job.title.ilike(like), Job.company.ilike(like), Job.location.ilike(like)))
                .order_by(Job.discovered_at.desc())
                .limit(limit)
            )
        return list(self.db.scalars(statement))

    def get_by_id(self, job_id: str) -> Job | None:
        return self.db.get(Job, job_id)

    def upsert_many(self, jobs: list[dict]) -> tuple[int, int]:
        created = 0
        updated = 0
        for job_data in jobs:
            existing = self.db.scalar(
                select(Job).where(
                    Job.source == job_data["source"],
                    Job.external_id == job_data["external_id"],
                )
            )
            if existing is None:
                self.db.add(Job(**job_data))
                created += 1
                continue

            for key, value in job_data.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.now(UTC)
            updated += 1

        self.db.commit()
        return created, updated


class ProcessingRunRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, run_type: str, source: str | None, metadata: dict | None = None) -> ProcessingRun:
        run = ProcessingRun(
            run_type=run_type,
            status="running",
            source=source,
            extra_metadata=metadata,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def finish(
        self,
        run: ProcessingRun,
        *,
        status: str,
        records_seen: int,
        records_created: int,
        records_updated: int,
        error: str | None = None,
    ) -> ProcessingRun:
        run.status = status
        run.records_seen = records_seen
        run.records_created = records_created
        run.records_updated = records_updated
        run.error = error
        run.finished_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(run)
        return run
