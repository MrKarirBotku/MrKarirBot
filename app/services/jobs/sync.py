import hashlib
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.job import Job
from app.sources.base import JobSource, SourceJob
from app.sources.registry import get_job_sources


@dataclass
class SyncStats:
    fetched: int = 0
    created: int = 0
    updated: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, int | list[str]]:
        return asdict(self)


def create_fingerprint(job: SourceJob) -> str:
    identity = f"{job.title}|{job.company}|{job.location}"
    normalized = re.sub(r"[^a-z0-9]+", " ", identity.casefold()).strip()
    return hashlib.sha256(normalized.encode()).hexdigest()


class JobSyncService:
    def __init__(self, sources: list[JobSource] | None = None) -> None:
        self.sources = sources or get_job_sources()

    async def sync(self, db: AsyncSession, query: str = "", limit: int = 100) -> SyncStats:
        stats = SyncStats()
        now = datetime.now(UTC)

        for source in self.sources:
            try:
                listings = await source.fetch(query=query, limit=limit)
            # A failed provider must not block synchronization from healthy providers.
            except Exception as exc:  # noqa: BLE001
                stats.errors.append(f"{source.name}: {type(exc).__name__}")
                continue

            stats.fetched += len(listings)
            for listing in listings:
                fingerprint = create_fingerprint(listing)
                job = await db.scalar(
                    select(Job)
                    .where(
                        or_(
                            Job.fingerprint == fingerprint,
                            and_(
                                Job.source_name == listing.source_name,
                                Job.external_id == listing.external_id,
                            ),
                        )
                    )
                    .limit(1)
                )
                values = self._job_values(listing, fingerprint, now)
                if job is None:
                    db.add(Job(**values))
                    stats.created += 1
                else:
                    for key, value in values.items():
                        setattr(job, key, value)
                    stats.updated += 1

        await db.commit()
        return stats

    @staticmethod
    def _job_values(
        listing: SourceJob,
        fingerprint: str,
        now: datetime,
    ) -> dict[str, object]:
        return {
            "external_id": listing.external_id,
            "fingerprint": fingerprint,
            "title": listing.title,
            "company": listing.company,
            "location": listing.location,
            "description": listing.description,
            "job_type": listing.job_type,
            "is_remote": listing.is_remote,
            "work_system": "remote" if listing.is_remote else None,
            "source_name": listing.source_name,
            "source_url": str(listing.source_url),
            "apply_url": str(listing.source_url),
            "published_at": listing.published_at or now,
            "expires_at": listing.expires_at,
            "last_seen_at": now,
            "is_active": True,
            "is_verified": False,
            "is_demo": False,
            "verification_status": "published",
            "fraud_risk_level": "unknown",
        }
