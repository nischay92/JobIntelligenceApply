"""create generated answers

Revision ID: 20260603_0006
Revises: 20260603_0005
Create Date: 2026-06-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260603_0006"
down_revision: str | None = "20260603_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "generated_answers",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("resume_id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("content_type", sa.String(length=64), nullable=False),
        sa.Column("prompt_label", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("vector_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_generated_answers_user_job_type",
        "generated_answers",
        ["user_id", "job_id", "content_type"],
    )
    op.create_index("ix_generated_answers_user_status", "generated_answers", ["user_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_generated_answers_user_status", table_name="generated_answers")
    op.drop_index("ix_generated_answers_user_job_type", table_name="generated_answers")
    op.drop_table("generated_answers")
