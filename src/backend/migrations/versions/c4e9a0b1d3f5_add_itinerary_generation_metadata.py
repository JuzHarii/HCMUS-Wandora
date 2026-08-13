"""add itinerary generation metadata

Revision ID: c4e9a0b1d3f5
Revises: f90ac4e2d112
Create Date: 2026-08-13 22:15:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4e9a0b1d3f5"
down_revision: Union[str, Sequence[str], None] = "f90ac4e2d112"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("workspaces", sa.Column("itinerary_source", sa.String(length=32), nullable=True))
    op.add_column("workspaces", sa.Column("itinerary_generated_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("workspaces", "itinerary_generated_at")
    op.drop_column("workspaces", "itinerary_source")
