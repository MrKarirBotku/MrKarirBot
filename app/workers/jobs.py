import asyncio
import logging

from app.core.config import get_settings
from app.database.session import AsyncSessionLocal
from app.services.jobs.sync import JobSyncService
from app.services.notifications.channel import TelegramChannelPublisher

logger = logging.getLogger(__name__)


async def run_job_cycle() -> None:
    settings = get_settings()
    async with AsyncSessionLocal() as db:
        stats = await JobSyncService().sync(db)
        published = await TelegramChannelPublisher().publish_pending(
            db,
            limit=settings.job_publish_batch_size,
        )
    logger.info("job_cycle_complete stats=%s published=%s", stats.to_dict(), published)


async def run_forever() -> None:
    settings = get_settings()
    while True:
        try:
            await run_job_cycle()
        except Exception:
            logger.exception("job_cycle_failed")
        await asyncio.sleep(settings.job_sync_interval_minutes * 60)
