from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, or_, select
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
        location: str | None = None,
        country: str | None = None,
        work_system: str | None = None,
        employment_type: str | None = None,
        experience_level: str | None = None,
        salary_min: int | None = None,
        currency: str | None = None,
        source: str | None = None,
        published_after: datetime | None = None,
        sort: str = "newest",
    ) -> tuple[list[Job], int]:
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
        if location:
            stmt = stmt.where(Job.location.ilike(f"%{location}%"))
        if country:
            stmt = stmt.where(Job.country.ilike(country))
        if work_system:
            stmt = stmt.where(Job.work_system == work_system)
        if employment_type:
            stmt = stmt.where(Job.job_type == employment_type)
        if experience_level:
            stmt = stmt.where(Job.experience_level == experience_level)
        if salary_min is not None:
            stmt = stmt.where(Job.salary_max.is_not(None), Job.salary_max >= salary_min)
        if currency:
            stmt = stmt.where(Job.salary_currency == currency.upper())
        if source:
            stmt = stmt.where(Job.source_name.ilike(source))
        if published_after:
            stmt = stmt.where(Job.published_at >= published_after)

        total = int(await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0)
        if sort == "salary":
            stmt = stmt.order_by(Job.salary_max.desc().nullslast(), Job.published_at.desc())
        elif sort == "relevance" and query:
            stmt = stmt.order_by(Job.published_at.desc().nullslast())
        else:
            stmt = stmt.order_by(Job.published_at.desc().nullslast(), Job.id.desc())
        result = await db.execute(stmt.offset(offset).limit(limit))
        return list(result.scalars().all()), total

    async def get(self, db: AsyncSession, job_id: UUID) -> Job | None:
        return await db.scalar(
            select(Job).where(
                Job.id == job_id,
                Job.is_active.is_(True),
                Job.is_demo.is_(False),
                Job.fraud_risk_level != "high",
            )
        )
