import secrets
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.bot.webhook import process_telegram_update
from app.core.config import get_settings

router = APIRouter(prefix="/telegram", tags=["telegram"])


class TelegramUpdate(BaseModel):
    """Minimal envelope validation while preserving Telegram update fields."""

    model_config = ConfigDict(extra="allow")
    update_id: int = Field(ge=0)

    def as_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    content_length: int | None = Header(default=None, alias="Content-Length"),
) -> dict[str, str]:
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise HTTPException(status_code=503, detail="Telegram bot token belum dikonfigurasi")
    if not settings.telegram_webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook secret belum dikonfigurasi")
    received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not secrets.compare_digest(received_secret, settings.telegram_webhook_secret):
        raise HTTPException(status_code=403, detail="Webhook secret tidak valid")
    if content_length is not None and content_length > 1_000_000:
        raise HTTPException(status_code=413, detail="Payload webhook terlalu besar")
    try:
        update = TelegramUpdate.model_validate(await request.json())
    except (ValidationError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Payload Telegram tidak valid") from exc
    background_tasks.add_task(process_telegram_update, update.as_payload())
    return {"status": "accepted"}
