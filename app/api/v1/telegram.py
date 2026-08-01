import secrets

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from telegram import Bot
from telegram.error import TelegramError

from app.bot.webhook import process_telegram_update
from app.core.config import get_settings

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.get("/status")
async def telegram_public_status() -> dict[str, bool | str | None]:
    """Return public Telegram connection metadata without exposing credentials."""

    settings = get_settings()
    channel_url = (
        f"https://t.me/{settings.telegram_channel_id.removeprefix('@')}"
        if settings.telegram_channel_id.startswith("@")
        else None
    )
    if not settings.telegram_bot_token:
        return {
            "enabled": False,
            "bot_username": None,
            "bot_url": None,
            "channel_url": channel_url,
        }

    try:
        identity = await Bot(settings.telegram_bot_token).get_me()
    except TelegramError:
        return {
            "enabled": False,
            "bot_username": None,
            "bot_url": None,
            "channel_url": channel_url,
        }

    bot_username = identity.username
    return {
        "enabled": bool(bot_username),
        "bot_username": bot_username,
        "bot_url": f"https://t.me/{bot_username}?start=website" if bot_username else None,
        "channel_url": channel_url,
    }


@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks) -> dict[str, str]:
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise HTTPException(status_code=503, detail="Telegram bot token belum dikonfigurasi")
    if settings.telegram_webhook_secret:
        received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if not secrets.compare_digest(received_secret, settings.telegram_webhook_secret):
            raise HTTPException(status_code=403, detail="Webhook secret tidak valid")
    payload = await request.json()
    background_tasks.add_task(process_telegram_update, payload)
    return {"status": "accepted"}
