from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import require_admin
from app.database.session import get_db
from app.schemas.job import JobPage, JobRead
from app.services.jobs.service import JobService
from app.services.jobs.sync import JobSyncService
from app.services.notifications.channel import TelegramChannelPublisher

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _database_unavailable() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Layanan lowongan sementara tidak tersedia",
    )


@router.get("", response_model=JobPage)
async def search_jobs(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str = Query(default="", max_length=120),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    remote: bool = False,
    location: str | None = Query(default=None, max_length=120),
    country: str | None = Query(default=None, max_length=80),
    work_system: Literal["remote", "hybrid", "onsite"] | None = None,
    employment_type: Literal[
        "full_time", "part_time", "contract", "freelance", "internship", "temporary"
    ]
    | None = None,
    experience_level: Literal[
        "fresh_graduate", "no_experience", "entry", "mid", "senior", "manager"
    ]
    | None = None,
    salary_min: int | None = Query(default=None, ge=0),
    currency: str | None = Query(default=None, min_length=3, max_length=3),
    source: str | None = Query(default=None, max_length=80),
    published_within_days: int | None = Query(default=None, ge=1, le=365),
    sort: Literal["newest", "relevance", "salary"] = "newest",
) -> JobPage:
    try:
        jobs, total = await JobService().search(
            db,
            query=q,
            limit=limit,
            offset=offset,
            remote_only=remote,
            location=location,
            country=country,
            work_system=work_system,
            employment_type=employment_type,
            experience_level=experience_level,
            salary_min=salary_min,
            currency=currency,
            source=source,
            published_after=(
                datetime.now(UTC) - timedelta(days=published_within_days)
                if published_within_days
                else None
            ),
            sort=sort,
        )
    except (SQLAlchemyError, OSError) as exc:
        raise _database_unavailable() from exc
    return JobPage(
        items=[JobRead.model_validate(job) for job in jobs],
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + len(jobs) < total,
    )


@router.post("/sync/run", status_code=status.HTTP_200_OK)
async def sync_jobs(
    db: Annotated[AsyncSession, Depends(get_db)],
    _admin: Annotated[dict[str, str | UUID | None], Depends(require_admin)],
    limit: int = Query(default=100, ge=1, le=500),
) -> dict[str, int | list[str]]:
    stats = await JobSyncService().sync(db, limit=limit)
    return stats.to_dict()


@router.post("/publish/run", status_code=status.HTTP_200_OK)
async def publish_jobs(
    db: Annotated[AsyncSession, Depends(get_db)],
    _admin: Annotated[dict[str, str | UUID | None], Depends(require_admin)],
    limit: int = Query(default=10, ge=1, le=50),
) -> dict[str, int]:
    published = await TelegramChannelPublisher().publish_pending(db, limit=limit)
    return {"published": published}


@router.get("/{job_id}", response_model=JobRead)
async def get_job(
    job_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobRead:
    try:
        job = await JobService().get(db, job_id)
    except (SQLAlchemyError, OSError) as exc:
        raise _database_unavailable() from exc
    if job is None:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    return JobRead.model_validate(job)
