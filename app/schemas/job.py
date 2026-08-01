from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class JobRead(BaseModel):
    id: UUID
    external_id: str | None = None
    title: str
    company: str
    location: str | None = None
    city: str | None = None
    province: str | None = None
    country: str | None = None
    description: str = ""
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    job_type: str | None = None
    work_system: str | None = None
    experience_level: str | None = None
    education_level: str | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    salary_is_visible: bool = False
    skills: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)
    is_remote: bool = False
    source_name: str
    source_url: HttpUrl
    apply_url: HttpUrl | None = None
    published_at: datetime
    expires_at: datetime | None = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class JobPage(BaseModel):
    items: list[JobRead]
    total: int
    limit: int
    offset: int
    has_more: bool
