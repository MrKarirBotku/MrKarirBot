from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.job import JobRead
from app.services.jobs.service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRead])
async def search_jobs(
    q: str = Query(default="", max_length=120),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[JobRead]:
    jobs = await JobService().search(db, query=q, limit=limit)
    return [JobRead.model_validate(job) for job in jobs]
