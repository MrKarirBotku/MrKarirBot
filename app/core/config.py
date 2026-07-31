from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MrKarirBot"
    environment: str = "development"
    secret_key: str = Field(default="change-me", min_length=8)
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mrkarirbot"
    redis_url: str = "redis://localhost:6379/0"
    telegram_bot_token: str = ""
    telegram_webhook_url: str = ""
    telegram_webhook_secret: str = ""
    telegram_channel_id: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-terra"
    job_sync_interval_minutes: int = Field(default=30, ge=5, le=1440)
    job_publish_batch_size: int = Field(default=10, ge=1, le=50)
    rate_limit: str = "60/minute"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
