from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import ARRAY, Boolean, DateTime, Numeric, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    external_id: Mapped[str | None] = mapped_column(Text)
    fingerprint: Mapped[str | None] = mapped_column("deduplication_key", Text)
    title: Mapped[str] = mapped_column(Text)
    company: Mapped[str] = mapped_column("company_name", Text)
    location: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(Text)
    province: Mapped[str | None] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    salary_min: Mapped[Decimal | None] = mapped_column(Numeric)
    salary_max: Mapped[Decimal | None] = mapped_column(Numeric)
    job_type: Mapped[str | None] = mapped_column("employment_type", Text)
    experience_level: Mapped[str | None] = mapped_column(Text)
    education_level: Mapped[str | None] = mapped_column(Text)
    salary_currency: Mapped[str | None] = mapped_column(Text)
    salary_period: Mapped[str | None] = mapped_column(Text)
    salary_is_visible: Mapped[bool] = mapped_column(Boolean, default=False)
    skills: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    benefits: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    work_system: Mapped[str | None] = mapped_column(Text)
    source_name: Mapped[str] = mapped_column("source", Text)
    source_url: Mapped[str] = mapped_column(Text)
    apply_url: Mapped[str | None] = mapped_column(Text)
    canonical_url: Mapped[str | None] = mapped_column(Text)
    normalized_title: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_status: Mapped[str] = mapped_column(Text, default="imported")
    fraud_risk_level: Mapped[str] = mapped_column(Text, default="unknown")
    channel_posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
