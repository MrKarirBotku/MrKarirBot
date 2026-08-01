from telegram import Update
from telegram.ext import ContextTypes

from app.core.config import get_settings
from app.database.session import AsyncSessionLocal
from app.services.notifications.channel import TelegramChannelPublisher


def is_telegram_admin(update: Update) -> bool:
    user = update.effective_user
    return user is not None and user.id in get_settings().telegram_admin_id_set


async def _reject_non_admin(update: Update) -> bool:
    if is_telegram_admin(update):
        return False
    if update.effective_message:
        await update.effective_message.reply_text("Perintah ini hanya tersedia untuk admin.")
    return True


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_non_admin(update):
        return
    settings = get_settings()
    channel_status = "aktif" if TelegramChannelPublisher().enabled else "belum aktif"
    await update.effective_message.reply_text(
        "Panel Admin MrKarirBot\n\n"
        f"Channel: {settings.telegram_channel_id or '-'} ({channel_status})\n"
        f"Batch publikasi: {settings.job_publish_batch_size}\n\n"
        "Perintah:\n"
        "/publish — kirim lowongan tertunda ke channel"
    )


async def publish_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_non_admin(update):
        return
    settings = get_settings()
    publisher = TelegramChannelPublisher()
    if not publisher.enabled:
        await update.effective_message.reply_text("Publikasi channel belum dikonfigurasi.")
        return

    await update.effective_message.reply_text("Memproses lowongan tertunda…")
    async with AsyncSessionLocal() as db:
        published = await publisher.publish_pending(db, limit=settings.job_publish_batch_size)
    await update.effective_message.reply_text(
        f"Selesai. {published} lowongan dipublikasikan ke {settings.telegram_channel_id}."
    )
