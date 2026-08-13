"""Điểm vào của ứng dụng FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.core.config import get_settings
from app.db.session import engine


def create_app() -> FastAPI:
    """Khởi tạo ứng dụng FastAPI."""

    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        # Vite chooses the next available port when 5173 is occupied.  Keep
        # development flexible without allowing arbitrary remote origins.
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+$",
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
    app.include_router(api_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/db")
    def database_health() -> dict[str, str]:
        """Kiểm tra ứng dụng kết nối được PostgreSQL Supabase hay không."""

        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Không thể kết nối database.",
            ) from exc
        return {"status": "ok", "database": "connected"}

    return app


app = create_app()
