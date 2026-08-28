"""add itinerary versions

Revision ID: e5f0a1b2c3d4
Revises: c4e9a0b1d3f5
Create Date: 2026-08-13 22:35:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5f0a1b2c3d4"
down_revision: Union[str, Sequence[str], None] = "c4e9a0b1d3f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "itinerary_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("generation_source", sa.String(length=32), nullable=True),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_itinerary_versions_workspace_id", "itinerary_versions", ["workspace_id"])


def downgrade() -> None:
    op.drop_index("ix_itinerary_versions_workspace_id", table_name="itinerary_versions")
    op.drop_table("itinerary_versions")
