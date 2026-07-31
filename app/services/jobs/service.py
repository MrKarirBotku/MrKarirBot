from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.job import Job


class JobService:
    async def search(
        self,
        db: AsyncSession,
        query: str = "",
        limit: int = 10,
        offset: int = 0,
        remote_only: bool = False,
    ) -> list[Job]:
        now = datetime.now(UTC)
        stmt = select(Job).where(
            Job.is_active.is_(True),
            Job.is_demo.is_(False),
            Job.fraud_risk_level != "high",
            or_(Job.expires_at.is_(None), Job.expires_at >= now),
        )
        if query:
            like = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Job.title.ilike(like),
                    Job.company.ilike(like),
                    Job.location.ilike(like),
                    Job.description.ilike(like),
                )
            )
        if remote_only:
            stmt = stmt.where(Job.is_remote.is_(True))
        stmt = stmt.order_by(Job.published_at.desc().nullslast(), Job.id.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get(self, db: AsyncSession, job_id: UUID) -> Job | None:
        return await db.scalar(
            select(Job).where(
                Job.id == job_id,
                Job.is_active.is_(True),
                Job.is_demo.is_(False),
                Job.fraud_risk_level != "high",
            )
        )
