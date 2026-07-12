from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from app.core.config import get_settings
from app.bot.handlers.main import help_command, menu_callback, start, text_message


def build_application() -> Application:
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN wajib diisi untuk menjalankan bot")
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    return app
