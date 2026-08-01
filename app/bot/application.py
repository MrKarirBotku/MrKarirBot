from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from app.bot.handlers.main import (
    ats_command,
    company_command,
    help_command,
    interview_command,
    menu_callback,
    menu_command,
    privacy_command,
    remote_command,
    roadmap_command,
    salary_command,
    scam_command,
    search_command,
    start,
    text_message,
)
from app.core.config import get_settings


def build_application() -> Application:
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN wajib diisi untuk menjalankan bot")
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cari", search_command))
    app.add_handler(CommandHandler("remote", remote_command))
    app.add_handler(CommandHandler("ats", ats_command))
    app.add_handler(CommandHandler("interview", interview_command))
    app.add_handler(CommandHandler("roadmap", roadmap_command))
    app.add_handler(CommandHandler("salary", salary_command))
    app.add_handler(CommandHandler("company", company_command))
    app.add_handler(CommandHandler("scam", scam_command))
    app.add_handler(CommandHandler("privacy", privacy_command))
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    return app
