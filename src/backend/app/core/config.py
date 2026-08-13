"""Cấu hình ứng dụng và biến môi trường."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    """Tập hợp cấu hình runtime cho ứng dụng."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "HCMUS-Wandora"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = False
    database_url: str = Field(alias="DATABASE_URL")
    db_pool_mode: Literal["session", "transaction"] = Field(default="session", alias="DB_POOL_MODE")
    db_pool_size: int = Field(default=5, ge=1, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=5, ge=0, alias="DB_MAX_OVERFLOW")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.6-flash", alias="GEMINI_MODEL")
    gemini_timeout_seconds: int = Field(default=25, ge=5, le=120, alias="GEMINI_TIMEOUT_SECONDS")
    jwt_secret_key: str = Field(min_length=32, alias="JWT_SECRET_KEY")
    jwt_expire_minutes: int = Field(default=10080, ge=15, alias="JWT_EXPIRE_MINUTES")

    @field_validator("database_url")
    @classmethod
    def require_postgres_driver(cls, value: str) -> str:
        """Chỉ cho phép PostgreSQL (Supabase), không âm thầm quay về SQLite."""

        if value.startswith("postgresql+psycopg://"):
            return value
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value.removeprefix("postgresql://")
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value.removeprefix("postgres://")
        raise ValueError("DATABASE_URL phải là URI PostgreSQL của Supabase.")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Trả về settings đã được cache để tránh đọc lại nhiều lần."""

    return Settings()
