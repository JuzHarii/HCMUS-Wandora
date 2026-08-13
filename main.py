"""Điểm vào của ứng dụng FastAPI."""

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.db.session import init_db


def create_app() -> FastAPI:
    """Khởi tạo ứng dụng FastAPI."""

    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.include_router(api_router)

    @app.on_event("startup")
    def _startup() -> None:
        init_db()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
