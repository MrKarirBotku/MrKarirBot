import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_development_defaults() -> None:
    with pytest.raises(ValidationError, match="Konfigurasi production tidak aman"):
        Settings(environment="production")


def test_production_accepts_explicit_secure_configuration() -> None:
    settings = Settings(
        environment="production",
        secret_key="s" * 64,
        database_url="postgresql+asyncpg://postgres:password@db.example.com:5432/postgres",
        redis_url="rediss://default:password@redis.example.com:6379/0",
        site_url="https://mrkarirai.web.id",
        app_url="https://mrkarirai.web.id",
        cors_origins="https://mrkarirai.web.id",
        supabase_url="https://project-ref.supabase.co",
        supabase_publishable_key="sb_publishable_test",
        telegram_bot_token="",
    )

    assert settings.environment == "production"
