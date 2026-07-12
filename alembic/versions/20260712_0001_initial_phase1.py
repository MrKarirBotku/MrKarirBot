"""initial phase 1 schema

Revision ID: 20260712_0001
Revises:
Create Date: 2026-07-12
"""
from alembic import op
import sqlalchemy as sa

revision = "20260712_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("telegram_id", sa.Integer(), unique=True), sa.Column("email", sa.String(255), unique=True), sa.Column("full_name", sa.String(255), nullable=False), sa.Column("hashed_password", sa.String(255)), sa.Column("role", sa.String(50), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])
    op.create_table("jobs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("title", sa.String(255), nullable=False), sa.Column("company", sa.String(255), nullable=False), sa.Column("location", sa.String(255), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("salary_min", sa.Integer()), sa.Column("salary_max", sa.Integer()), sa.Column("source_url", sa.String(500)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_jobs_title", "jobs", ["title"])
    op.create_index("ix_jobs_company", "jobs", ["company"])
    op.create_index("ix_jobs_location", "jobs", ["location"])
    op.create_table("audit_logs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("actor", sa.String(255), nullable=False), sa.Column("action", sa.String(120), nullable=False), sa.Column("metadata_json", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("user_profiles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True), sa.Column("headline", sa.String(255)), sa.Column("phone", sa.String(50)), sa.Column("location", sa.String(255)), sa.Column("skills", sa.Text()), sa.Column("experience_summary", sa.Text()), sa.Column("cv_file_id", sa.String(255)), sa.Column("resume_file_id", sa.String(255)), sa.Column("portfolio_url", sa.String(500)), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("job_bookmarks", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")), sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("application_trackers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")), sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="SET NULL")), sa.Column("company", sa.String(255), nullable=False), sa.Column("position", sa.String(255), nullable=False), sa.Column("status", sa.String(50), nullable=False), sa.Column("notes", sa.Text()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_table("application_trackers")
    op.drop_table("job_bookmarks")
    op.drop_table("user_profiles")
    op.drop_table("audit_logs")
    op.drop_table("jobs")
    op.drop_table("users")
