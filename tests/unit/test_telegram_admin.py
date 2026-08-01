from telegram import Update, User

from app.bot.handlers.admin import is_telegram_admin
from app.core.config import Settings


def test_admin_ids_are_parsed_and_invalid_values_are_ignored() -> None:
    settings = Settings(telegram_admin_ids="8780667139, 123, invalid")
    assert settings.telegram_admin_id_set == {8780667139, 123}


def test_configured_user_is_telegram_admin(monkeypatch) -> None:
    settings = Settings(telegram_admin_ids="8780667139")
    monkeypatch.setattr("app.bot.handlers.admin.get_settings", lambda: settings)
    update = Update(update_id=1)
    update._effective_user = User(id=8780667139, first_name="Admin", is_bot=False)
    assert is_telegram_admin(update)
