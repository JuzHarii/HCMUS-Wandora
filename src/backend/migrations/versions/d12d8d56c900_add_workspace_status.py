"""add workspace status

Revision ID: d12d8d56c900
Revises: 36c21682e487
Create Date: 2026-08-13 15:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d12d8d56c900"
down_revision: Union[str, Sequence[str], None] = "36c21682e487"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "workspaces",
        sa.Column("status", sa.String(length=32), nullable=False, server_default="Draft"),
    )
    op.alter_column("workspaces", "status", server_default=None)


def downgrade() -> None:
    op.drop_column("workspaces", "status")
