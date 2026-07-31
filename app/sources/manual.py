from app.sources.base import JobSource, SourceJob


class ManualJobSource(JobSource):
    name = "manual"

    async def fetch(self, query: str = "", limit: int = 100) -> list[SourceJob]:
        return []
