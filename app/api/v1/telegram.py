from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from app.core.config import get_settings
from app.bot.webhook import process_telegram_update

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks) -> dict[str, str]:
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise HTTPException(status_code=503, detail="Telegram bot token belum dikonfigurasi")
    payload = await request.json()
    background_tasks.add_task(process_telegram_update, payload)
    return {"status": "accepted"}
