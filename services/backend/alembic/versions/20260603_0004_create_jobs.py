"""create jobs and processing runs

Revision ID: 20260603_0004
Revises: 20260603_0003
Create Date: 2026-06-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260603_0004"
down_revision: str | None = "20260603_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("employment_type", sa.String(length=128), nullable=True),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("salary_currency", sa.String(length=16), nullable=True),
        sa.Column("description_url", sa.Text(), nullable=False),
        sa.Column("apply_url", sa.Text(), nullable=True),
        sa.Column("raw_description", sa.Text(), nullable=True),
        sa.Column("parsed_description", sa.JSON(), nullable=True),
        sa.Column("required_skills", sa.JSON(), nullable=True),
        sa.Column("preferred_skills", sa.JSON(), nullable=True),
        sa.Column("technology_stack", sa.JSON(), nullable=True),
        sa.Column("sponsorship_hints", sa.JSON(), nullable=True),
        sa.Column("security_clearance_required", sa.Boolean(), nullable=False),
        sa.Column("remote_policy", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source", "external_id", name="uq_jobs_source_external_id"),
        sa.UniqueConstraint("description_url", name="uq_jobs_description_url"),
    )
    op.create_index("ix_jobs_company_title", "jobs", ["company", "title"])
    op.create_index("ix_jobs_status_discovered", "jobs", ["status", "discovered_at"])

    op.create_table(
        "processing_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("run_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_seen", sa.Integer(), nullable=False),
        sa.Column("records_created", sa.Integer(), nullable=False),
        sa.Column("records_updated", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
    )
    op.create_index("ix_processing_runs_type_started", "processing_runs", ["run_type", "started_at"])
    op.create_index("ix_processing_runs_status_started", "processing_runs", ["status", "started_at"])


def downgrade() -> None:
    op.drop_index("ix_processing_runs_status_started", table_name="processing_runs")
    op.drop_index("ix_processing_runs_type_started", table_name="processing_runs")
    op.drop_table("processing_runs")
    op.drop_index("ix_jobs_status_discovered", table_name="jobs")
    op.drop_index("ix_jobs_company_title", table_name="jobs")
    op.drop_table("jobs")
