"""Sao chép dữ liệu Wandora từ SQLite local sang PostgreSQL/Supabase.

Ví dụ:
    python scripts/migrate_sqlite_to_supabase.py \
      --database-url "postgresql+psycopg://..."

Script không ghi đè dữ liệu đích: nếu một bảng Wandora trên Supabase đã có
dữ liệu, script sẽ dừng để tránh nhập trùng ngoài ý muốn.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect, select

# Windows PowerShell legacy code pages cannot print Vietnamese argparse help.
# Prefer UTF-8 when the active output stream supports reconfiguration.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# `python scripts/...` makes `scripts/` the first import directory, so add the
# backend package root before importing the application package.
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPOSITORY_ROOT / "src" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import models  # noqa: F401 - đăng ký toàn bộ model vào metadata
from app.db.base import Base


def normalise_postgres_url(url: str) -> str:
    """Đổi URI Supabase thông thường sang dialect psycopg của SQLAlchemy."""

    if url.startswith("postgresql+psycopg://"):
        return url
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.removeprefix("postgres://")
    raise ValueError("--database-url phải là URI PostgreSQL/Supabase.")


def migrate(source_path: Path, database_url: str) -> None:
    if not source_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy SQLite database: {source_path}")

    source_engine = create_engine(f"sqlite:///{source_path.resolve().as_posix()}")
    target_engine = create_engine(normalise_postgres_url(database_url), pool_pre_ping=True)
    source_tables = set(inspect(source_engine).get_table_names())

    target_tables = set(inspect(target_engine).get_table_names())
    expected_tables = {table.name for table in Base.metadata.sorted_tables}
    missing_tables = expected_tables - target_tables
    if missing_tables:
        missing = ", ".join(sorted(missing_tables))
        raise RuntimeError(
            f"Supabase chưa có schema Wandora ({missing}). "
            "Hãy chạy `alembic -c src/backend/alembic.ini upgrade head` trước."
        )

    # Giữ thứ tự phụ thuộc khóa ngoại do SQLAlchemy tính sẵn.
    with target_engine.begin() as target_connection:
        for table in Base.metadata.sorted_tables:
            if table.name not in source_tables:
                continue
            if target_connection.execute(select(table).limit(1)).first() is not None:
                raise RuntimeError(
                    f"Bảng đích '{table.name}' đã có dữ liệu. Dừng để tránh nhập trùng."
                )

    totals: dict[str, int] = {}
    with source_engine.connect() as source_connection, target_engine.begin() as target_connection:
        for table in Base.metadata.sorted_tables:
            if table.name not in source_tables:
                continue
            rows = [dict(row) for row in source_connection.execute(select(table)).mappings()]
            if rows:
                target_connection.execute(table.insert(), rows)
            totals[table.name] = len(rows)

    summary = ", ".join(f"{name}: {count}" for name, count in totals.items()) or "không có bảng Wandora"
    print(f"Đã chuyển dữ liệu thành công. {summary}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chuyển SQLite Wandora sang Supabase PostgreSQL")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("backups/wandora-pre-supabase-migration.db"),
        help="Đường dẫn SQLite nguồn (mặc định: backup trước migration)",
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL"),
        help="Supabase PostgreSQL URI; mặc định đọc DATABASE_URL",
    )
    args = parser.parse_args()
    if not args.database_url:
        parser.error("cần --database-url hoặc biến môi trường DATABASE_URL")
    migrate(args.source, args.database_url)


if __name__ == "__main__":
    main()
