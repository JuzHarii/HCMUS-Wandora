from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cấu hình chạy ứng dụng, đọc từ biến môi trường hoặc file .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Wandora Backend"
    debug: bool = False
    database_url: str = "sqlite:///./wandora.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"
    jwt_secret_key: str = "wandora_super_secret_jwt_key_2026_change_in_prod"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440



@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Trả về cấu hình dùng chung toàn ứng dụng."""
    return Settings()
