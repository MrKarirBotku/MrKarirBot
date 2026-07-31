from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel, HttpUrl


class SourceJob(BaseModel):
    external_id: str
    title: str
    company: str
    location: str = "Remote"
    description: str
    salary_text: str | None = None
    job_type: str | None = None
    is_remote: bool = False
    source_name: str
    source_url: HttpUrl
    published_at: datetime | None = None
    expires_at: datetime | None = None


class JobSource(ABC):
    name: str

    @abstractmethod
    async def fetch(self, query: str = "", limit: int = 100) -> list[SourceJob]:
        """Fetch normalized, real job listings from a source."""
