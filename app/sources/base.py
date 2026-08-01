from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class SourceJob(BaseModel):
    external_id: str = Field(min_length=1, max_length=512)
    title: str = Field(min_length=1, max_length=500)
    company: str = Field(min_length=1, max_length=500)
    location: str = "Remote"
    description: str = Field(min_length=1, max_length=200_000)
    salary_text: str | None = None
    job_type: str | None = None
    is_remote: bool = False
    source_name: str = Field(min_length=1, max_length=120)
    source_url: HttpUrl
    published_at: datetime | None = None
    expires_at: datetime | None = None


class JobSource(ABC):
    name: str

    @abstractmethod
    async def fetch(self, query: str = "", limit: int = 100) -> list[SourceJob]:
        """Fetch normalized, real job listings from a source."""
