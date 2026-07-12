from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.job import Job


class JobService:
    async def search(self, db: AsyncSession, query: str = "", limit: int = 10) -> list[Job]:
        stmt = select(Job).limit(limit)
        if query:
            like = f"%{query}%"
            stmt = select(Job).where(Job.title.ilike(like) | Job.company.ilike(like)).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())
