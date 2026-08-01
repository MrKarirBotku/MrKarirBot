import asyncio
import logging
from datetime import UTC, datetime
from html import escape

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import RetryAfter, TelegramError

from app.core.config import get_settings
from app.database.models.job import Job

logger = logging.getLogger(__name__)


class TelegramChannelPublisher:
    def __init__(self) -> None:
        settings = get_settings()
        self.channel_id = settings.telegram_channel_id
        self.bot = Bot(settings.telegram_bot_token) if settings.telegram_bot_token else None

    @property
    def enabled(self) -> bool:
        return self.bot is not None and bool(self.channel_id)

    async def publish_pending(self, db: AsyncSession, limit: int = 5) -> int:
        if not self.enabled or self.bot is None:
            return 0

        result = await db.execute(
            select(Job)
            .where(
                Job.is_active.is_(True),
                Job.is_demo.is_(False),
                Job.fraud_risk_level != "high",
                or_(Job.expires_at.is_(None), Job.expires_at >= datetime.now(UTC)),
                Job.channel_posted_at.is_(None),
                Job.source_url.is_not(None),
            )
            .order_by(Job.published_at.desc().nullslast(), Job.id.desc())
            .limit(limit)
        )
        jobs = list(result.scalars().all())
        published = 0
        for job in jobs:
            try:
                await self._send(job)
            except RetryAfter as exc:
                # Telegram provides the retry delay; retry this job once without
                # aborting the remaining publication batch.
                await asyncio.sleep(float(exc.retry_after) + 0.1)
                try:
                    await self._send(job)
                except TelegramError as retry_exc:
                    logger.warning(
                        "channel_publish_failed job_id=%s error=%s",
                        job.id,
                        type(retry_exc).__name__,
                    )
                    continue
            except TelegramError as exc:
                logger.warning(
                    "channel_publish_failed job_id=%s error=%s",
                    job.id,
                    type(exc).__name__,
                )
                continue

            job.channel_posted_at = datetime.now(UTC)
            await db.commit()
            published += 1
        return published

    async def _send(self, job: Job) -> None:
        assert self.bot is not None
        await self.bot.send_message(
            chat_id=self.channel_id,
            text=self._format(job),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Lihat & Lamar", url=job.apply_url or job.source_url)]]
            ),
        )

    @staticmethod
    def _format(job: Job) -> str:
        remote = "🌍 Remote\n" if job.is_remote else ""
        job_type = f"💼 {escape(job.job_type)}\n" if job.job_type else ""
        return (
            "🔥 <b>LOWONGAN TERBARU</b>\n\n"
            f"<b>{escape(job.title)}</b>\n"
            f"🏢 {escape(job.company)}\n"
            f"📍 {escape(job.location or 'Lokasi tidak disebutkan')}\n"
            f"{remote}{job_type}"
            f"🔎 Sumber: {escape(job.source_name)}\n\n"
            "Lamar hanya melalui tautan sumber resmi. Jangan membayar biaya rekrutmen."
        )
