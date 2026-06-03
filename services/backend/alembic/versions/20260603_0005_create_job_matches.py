"""create job matches

Revision ID: 20260603_0005
Revises: 20260603_0004
Create Date: 2026-06-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260603_0005"
down_revision: str | None = "20260603_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "job_matches",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("resume_id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=False),
        sa.Column("skill_score", sa.Integer(), nullable=False),
        sa.Column("experience_score", sa.Integer(), nullable=False),
        sa.Column("education_score", sa.Integer(), nullable=False),
        sa.Column("missing_skills", sa.JSON(), nullable=False),
        sa.Column("missing_keywords", sa.JSON(), nullable=False),
        sa.Column("match_reasons", sa.JSON(), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("priority_reason", sa.Text(), nullable=False),
        sa.Column("scoring_model", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "resume_id", "job_id", name="uq_job_matches_user_resume_job"),
    )
    op.create_index(
        "ix_job_matches_user_priority_score",
        "job_matches",
        ["user_id", "priority", "overall_score"],
    )
    op.create_index("ix_job_matches_user_created", "job_matches", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_job_matches_user_created", table_name="job_matches")
    op.drop_index("ix_job_matches_user_priority_score", table_name="job_matches")
    op.drop_table("job_matches")
