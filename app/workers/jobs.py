import asyncio
import logging
import secrets
from collections.abc import Awaitable, Callable

from redis.asyncio import Redis, from_url

from app.core.config import get_settings
from app.database.session import AsyncSessionLocal
from app.services.jobs.sync import JobSyncService
from app.services.notifications.channel import TelegramChannelPublisher

logger = logging.getLogger(__name__)
CYCLE_LOCK_KEY = "mrkarirbot:jobs:cycle"
RELEASE_LOCK_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
  return redis.call('del', KEYS[1])
end
return 0
"""


async def run_job_cycle() -> None:
    settings = get_settings()
    async with AsyncSessionLocal() as db:
        stats = await JobSyncService().sync(db)
        published = await TelegramChannelPublisher().publish_pending(
            db,
            limit=settings.job_publish_batch_size,
        )
    logger.info("job_cycle_complete stats=%s published=%s", stats.to_dict(), published)


async def run_locked_job_cycle(
    redis_client: Redis | None = None,
    cycle: Callable[[], Awaitable[None]] = run_job_cycle,
) -> bool:
    """Run one cycle only when this worker owns the Redis lock."""

    settings = get_settings()
    client = redis_client or from_url(settings.redis_url, decode_responses=True)
    owns_client = redis_client is None
    lock_token = secrets.token_urlsafe(24)
    # A stale lock must eventually expire even if the container is terminated.
    lock_ttl = max(settings.job_sync_interval_minutes * 60, 300)

    try:
        acquired = await client.set(CYCLE_LOCK_KEY, lock_token, ex=lock_ttl, nx=True)
        if not acquired:
            logger.info("job_cycle_skipped reason=lock_held")
            return False

        try:
            await cycle()
            return True
        finally:
            await client.eval(RELEASE_LOCK_SCRIPT, 1, CYCLE_LOCK_KEY, lock_token)
    finally:
        if owns_client:
            await client.aclose()


async def run_forever() -> None:
    settings = get_settings()
    while True:
        try:
            await run_locked_job_cycle()
        except Exception:
            logger.exception("job_cycle_failed")
        await asyncio.sleep(settings.job_sync_interval_minutes * 60)
