from abc import ABC, abstractmethod
from app.schemas.job import JobRead


class JobSource(ABC):
    name: str

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[JobRead]:
        """Search jobs from a source."""
