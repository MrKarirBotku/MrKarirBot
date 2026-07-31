from datetime import datetime

from pydantic import BaseModel, HttpUrl


class JobRead(BaseModel):
    id: int
    external_id: str | None = None
    title: str
    company: str
    location: str
    description: str
    salary_min: int | None = None
    salary_max: int | None = None
    salary_text: str | None = None
    job_type: str | None = None
    is_remote: bool = False
    source_name: str
    source_url: HttpUrl | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None
    is_active: bool = True

    model_config = {"from_attributes": True}
