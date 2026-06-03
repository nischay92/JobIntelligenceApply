"""add resume parsing fields

Revision ID: 20260603_0003
Revises: 20260603_0002
Create Date: 2026-06-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260603_0003"
down_revision: str | None = "20260603_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("resumes", sa.Column("parsed_profile", sa.JSON(), nullable=True))
    op.add_column("resumes", sa.Column("plain_text", sa.Text(), nullable=True))
    op.add_column("resumes", sa.Column("vector_id", sa.String(length=255), nullable=True))
    op.add_column("resumes", sa.Column("parser_version", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("resumes", "parser_version")
    op.drop_column("resumes", "vector_id")
    op.drop_column("resumes", "plain_text")
    op.drop_column("resumes", "parsed_profile")
