"""add automatic job aggregation fields

Revision ID: 20260731_0002
Revises: 20260712_0001
Create Date: 2026-07-31
"""

import sqlalchemy as sa

from alembic import op

revision = "20260731_0002"
down_revision = "20260712_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("external_id", sa.String(255)))
    op.add_column("jobs", sa.Column("fingerprint", sa.String(64)))
    op.add_column("jobs", sa.Column("salary_text", sa.String(255)))
    op.add_column("jobs", sa.Column("job_type", sa.String(80)))
    op.add_column("jobs", sa.Column("is_remote", sa.Boolean(), server_default=sa.false()))
    op.add_column("jobs", sa.Column("source_name", sa.String(80), server_default="legacy"))
    op.add_column("jobs", sa.Column("published_at", sa.DateTime(timezone=True)))
    op.add_column("jobs", sa.Column("expires_at", sa.DateTime(timezone=True)))
    op.add_column(
        "jobs",
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.add_column("jobs", sa.Column("is_active", sa.Boolean(), server_default=sa.true()))
    op.add_column("jobs", sa.Column("channel_posted_at", sa.DateTime(timezone=True)))

    op.execute(
        "UPDATE jobs SET fingerprint = md5(lower(title || '|' || company || '|' || location)) "
        "WHERE fingerprint IS NULL"
    )
    op.alter_column("jobs", "fingerprint", nullable=False)
    op.alter_column("jobs", "source_name", nullable=False)

    op.create_index("ix_jobs_external_id", "jobs", ["external_id"])
    op.create_index("ix_jobs_fingerprint", "jobs", ["fingerprint"], unique=True)
    op.create_index("ix_jobs_job_type", "jobs", ["job_type"])
    op.create_index("ix_jobs_is_remote", "jobs", ["is_remote"])
    op.create_index("ix_jobs_source_name", "jobs", ["source_name"])
    op.create_index("ix_jobs_published_at", "jobs", ["published_at"])
    op.create_index("ix_jobs_expires_at", "jobs", ["expires_at"])
    op.create_index("ix_jobs_is_active", "jobs", ["is_active"])

    # Supabase exposes the public schema through its Data API. The backend uses
    # a server-side database role; browser clients must not bypass this API.
    for table in (
        "users",
        "jobs",
        "audit_logs",
        "user_profiles",
        "job_bookmarks",
        "application_trackers",
    ):
        op.execute(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY')


def downgrade() -> None:
    for table in (
        "users",
        "jobs",
        "audit_logs",
        "user_profiles",
        "job_bookmarks",
        "application_trackers",
    ):
        op.execute(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY')

    for index in (
        "ix_jobs_is_active",
        "ix_jobs_expires_at",
        "ix_jobs_published_at",
        "ix_jobs_source_name",
        "ix_jobs_is_remote",
        "ix_jobs_job_type",
        "ix_jobs_fingerprint",
        "ix_jobs_external_id",
    ):
        op.drop_index(index, table_name="jobs")

    for column in (
        "channel_posted_at",
        "is_active",
        "last_seen_at",
        "expires_at",
        "published_at",
        "source_name",
        "is_remote",
        "job_type",
        "salary_text",
        "fingerprint",
        "external_id",
    ):
        op.drop_column("jobs", column)
