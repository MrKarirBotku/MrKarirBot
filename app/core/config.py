from functools import lru_cache
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MrKarirBot"
    environment: str = "development"
    secret_key: str = Field(
        default="development-only-secret-change-before-production",
        min_length=32,
    )
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mrkarirbot"
    redis_url: str = "redis://localhost:6379/0"
    telegram_bot_token: str = ""
    telegram_webhook_url: str = ""
    telegram_webhook_secret: str = ""
    telegram_channel_id: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-terra"
    openai_timeout_seconds: float = Field(default=45, ge=5, le=120)
    supabase_url: str = ""
    supabase_publishable_key: str = ""
    job_sync_interval_minutes: int = Field(default=30, ge=5, le=1440)
    # Keep the public channel useful without flooding subscribers.
    job_publish_batch_size: int = Field(default=5, ge=1, le=5)
    rate_limit: str = "60/minute"
    site_url: str = "http://localhost:8000"
    app_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:8000"
    ads_txt_content: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Reject unsafe defaults before a production process starts serving traffic."""

        if self.environment.casefold() != "production":
            return self

        errors: list[str] = []
        if self.secret_key == "development-only-secret-change-before-production":
            errors.append("SECRET_KEY masih menggunakan nilai development")
        if len(self.secret_key) < 48:
            errors.append("SECRET_KEY production minimal 48 karakter")
        if not self.database_url.startswith("postgresql+asyncpg://"):
            errors.append("DATABASE_URL harus memakai PostgreSQL asyncpg")
        if not self.redis_url.startswith(("redis://", "rediss://")):
            errors.append("REDIS_URL tidak valid")
        if not self.site_url.startswith("https://"):
            errors.append("SITE_URL production harus HTTPS")
        if not self.app_url.startswith("https://"):
            errors.append("APP_URL production harus HTTPS")
        if not self.supabase_url.startswith("https://"):
            errors.append("SUPABASE_URL production wajib dikonfigurasi")
        if not self.supabase_publishable_key:
            errors.append("SUPABASE_PUBLISHABLE_KEY production wajib dikonfigurasi")
        if self.telegram_bot_token and not self.telegram_webhook_secret:
            errors.append("TELEGRAM_WEBHOOK_SECRET wajib saat Telegram bot aktif")

        if errors:
            raise ValueError("Konfigurasi production tidak aman: " + "; ".join(errors))
        return self

    @property
    def allowed_origins(self) -> list[str]:
        values = {self.site_url.rstrip("/"), self.app_url.rstrip("/")}
        values.update(item.strip().rstrip("/") for item in self.cors_origins.split(","))
        return sorted(item for item in values if item)

    @property
    def allowed_hosts(self) -> list[str]:
        hosts = {
            "localhost",
            "127.0.0.1",
            "testserver",
            "mrkarirbot",
            "*.railway.app",
        }
        for value in self.allowed_origins:
            if hostname := urlparse(value).hostname:
                hosts.add(hostname)
        hosts.add("mrkarirbot-production.up.railway.app")
        return sorted(hosts)


@lru_cache
def get_settings() -> Settings:
    return Settings()
