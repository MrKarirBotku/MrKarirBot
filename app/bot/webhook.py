from functools import lru_cache

from telegram import Update
from telegram.ext import Application

from app.bot.application import build_application


@lru_cache
def get_webhook_application() -> Application:
    return build_application()


async def process_telegram_update(payload: dict) -> None:
    application = get_webhook_application()
    if not application.bot_data.get("_mrkarirbot_initialized"):
        await application.initialize()
        application.bot_data["_mrkarirbot_initialized"] = True
    update = Update.de_json(payload, application.bot)
    await application.process_update(update)
