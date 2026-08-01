from functools import lru_cache
from urllib.parse import urlparse

from pydantic import Field
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
