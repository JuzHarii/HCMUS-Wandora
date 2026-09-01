"""Cấu hình ứng dụng và biến môi trường."""

from functools import lru_cache
from pathlib import Path

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
    database_url: str = Field(default="sqlite:///./wandora.db", alias="DATABASE_URL")
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    db_pool_mode: str = Field(default="session", alias="DB_POOL_MODE")
    db_pool_size: int = Field(default=5, ge=1, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=5, ge=0, alias="DB_MAX_OVERFLOW")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_timeout_seconds: int = Field(default=25, ge=5, le=120, alias="OPENAI_TIMEOUT_SECONDS")
    jwt_secret_key: str = Field(default="wandora_super_secret_jwt_key_2026_change_in_prod_32chars", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = Field(default=10080, ge=15, alias="JWT_EXPIRE_MINUTES")
    jwt_access_token_expire_minutes: int = 1440

    @field_validator("database_url")
    @classmethod
    def format_database_url(cls, value: str) -> str:
        """Hỗ trợ cả PostgreSQL (Supabase) và SQLite cho testing."""
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value.removeprefix("postgresql://")
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value.removeprefix("postgres://")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Trả về settings đã được cache để tránh đọc lại nhiều lần."""
    return Settings()
