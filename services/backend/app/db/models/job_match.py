from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JobMatch(Base):
    __tablename__ = "job_matches"
    __table_args__ = (
        UniqueConstraint("user_id", "resume_id", "job_id", name="uq_job_matches_user_resume_job"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id: Mapped[str] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_score: Mapped[int] = mapped_column(Integer, nullable=False)
    experience_score: Mapped[int] = mapped_column(Integer, nullable=False)
    education_score: Mapped[int] = mapped_column(Integer, nullable=False)
    missing_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    missing_keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    match_reasons: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    priority: Mapped[str] = mapped_column(String(32), nullable=False)
    priority_reason: Mapped[str] = mapped_column(Text, nullable=False)
    scoring_model: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    job = relationship("Job")
    resume = relationship("Resume")
    user = relationship("User")
