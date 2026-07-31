import secrets

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from app.bot.webhook import process_telegram_update
from app.core.config import get_settings

router = APIRouter(prefix="/telegram", tags=["telegram"])


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
