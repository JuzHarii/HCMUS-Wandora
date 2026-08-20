import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Đảm bảo src/backend nằm trong sys.path của Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import get_settings
from app.db.base import Base
import app.models  # noqa: F401

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """Lấy URL kết nối CSDL từ cấu hình ứng dụng."""
    return get_settings().database_url


def run_migrations_offline() -> None:
    """Chạy migration ở chế độ 'offline' (xuất SQL script trực tiếp không qua kết nối live)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Chạy migration ở chế độ 'online' (kết nối trực tiếp CSDL và áp dụng thay đổi)."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
