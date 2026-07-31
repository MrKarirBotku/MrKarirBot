from datetime import UTC, datetime
from html import escape

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from app.core.config import get_settings
from app.database.models.job import Job


class TelegramChannelPublisher:
    def __init__(self) -> None:
        settings = get_settings()
        self.channel_id = settings.telegram_channel_id
        self.bot = Bot(settings.telegram_bot_token) if settings.telegram_bot_token else None

    @property
    def enabled(self) -> bool:
        return self.bot is not None and bool(self.channel_id)

    async def publish_pending(self, db: AsyncSession, limit: int = 10) -> int:
        if not self.enabled or self.bot is None:
            return 0

        result = await db.execute(
            select(Job)
            .where(
                Job.is_active.is_(True),
                Job.channel_posted_at.is_(None),
                Job.source_url.is_not(None),
            )
            .order_by(Job.published_at.desc().nullslast(), Job.id.desc())
            .limit(limit)
        )
        jobs = list(result.scalars().all())
        published = 0
        for job in jobs:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=self._format(job),
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Lihat & Lamar", url=job.source_url)]]
                ),
            )
            job.channel_posted_at = datetime.now(UTC)
            published += 1
        await db.commit()
        return published

    @staticmethod
    def _format(job: Job) -> str:
        remote = "🌍 Remote\n" if job.is_remote else ""
        job_type = f"💼 {escape(job.job_type)}\n" if job.job_type else ""
        return (
            "🔥 <b>LOWONGAN TERBARU</b>\n\n"
            f"<b>{escape(job.title)}</b>\n"
            f"🏢 {escape(job.company)}\n"
            f"📍 {escape(job.location)}\n"
            f"{remote}{job_type}"
            f"🔎 Sumber: {escape(job.source_name)}\n\n"
            "Lamar hanya melalui tautan sumber resmi. Jangan membayar biaya rekrutmen."
        )
