from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import require_admin
from app.database.session import get_db
from app.schemas.job import JobRead
from app.services.jobs.service import JobService
from app.services.jobs.sync import JobSyncService
from app.services.notifications.channel import TelegramChannelPublisher

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRead])
async def search_jobs(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str = Query(default="", max_length=120),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    remote: bool = False,
) -> list[JobRead]:
    jobs = await JobService().search(
        db,
        query=q,
        limit=limit,
        offset=offset,
        remote_only=remote,
    )
    return [JobRead.model_validate(job) for job in jobs]


@router.post("/sync/run", status_code=status.HTTP_200_OK)
async def sync_jobs(
    db: Annotated[AsyncSession, Depends(get_db)],
    _admin: Annotated[dict[str, str], Depends(require_admin)],
    limit: int = Query(default=100, ge=1, le=500),
) -> dict[str, int | list[str]]:
    stats = await JobSyncService().sync(db, limit=limit)
    return stats.to_dict()


@router.post("/publish/run", status_code=status.HTTP_200_OK)
async def publish_jobs(
    db: Annotated[AsyncSession, Depends(get_db)],
    _admin: Annotated[dict[str, str], Depends(require_admin)],
    limit: int = Query(default=10, ge=1, le=50),
) -> dict[str, int]:
    published = await TelegramChannelPublisher().publish_pending(db, limit=limit)
    return {"published": published}


@router.get("/{job_id}", response_model=JobRead)
async def get_job(
    job_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobRead:
    job = await JobService().get(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    return JobRead.model_validate(job)
