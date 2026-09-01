from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api.router import api_router
from .core.config import get_settings
from .db.init_db import init_db
from .db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Quản lý vòng đời ứng dụng FastAPI: Khởi tạo DB khi khởi động."""
    _ = app
    init_db()
    yield


def create_app() -> FastAPI:
    """Khởi tạo ứng dụng FastAPI và gắn các thành phần nền tảng."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        """Trả trạng thái sống của dịch vụ."""
        return {"status": "ok"}

    @app.get("/health/db", tags=["system"])
    def database_health() -> dict[str, str]:
        """Kiểm tra ứng dụng kết nối được database hay không."""
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Không thể kết nối database.",
            ) from exc
        return {"status": "ok", "database": "connected"}

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        _ = request
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        _ = request
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
