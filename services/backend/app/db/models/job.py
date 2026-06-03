from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_jobs_source_external_id"),
        UniqueConstraint("description_url", name="uq_jobs_description_url"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    description_url: Mapped[str] = mapped_column(Text, nullable=False)
    apply_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_description: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    required_skills: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    preferred_skills: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    technology_stack: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    sponsorship_hints: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    security_clearance_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    remote_policy: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="discovered")
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
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
