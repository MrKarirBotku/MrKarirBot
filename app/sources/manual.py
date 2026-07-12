from app.schemas.job import JobRead
from app.sources.base import JobSource


class ManualJobSource(JobSource):
    name = "manual"

    async def search(self, query: str, limit: int = 10) -> list[JobRead]:
        return []
