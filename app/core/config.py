"""Cấu hình ứng dụng và biến môi trường."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Tập hợp cấu hình runtime cho ứng dụng."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "HCMUS-Wandora"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = False
    database_url: str = Field(default="sqlite:///./wandora.db", alias="DATABASE_URL")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Trả về settings đã được cache để tránh đọc lại nhiều lần."""

    return Settings()
