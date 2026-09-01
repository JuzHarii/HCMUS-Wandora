"""add packing item completion and assignment

Revision ID: a8b6c4d2e190
Revises: e5f0a1b2c3d4
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a8b6c4d2e190"
down_revision: Union[str, Sequence[str], None] = "e5f0a1b2c3d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("packing_items", sa.Column("assigned_to", sa.String(length=255), nullable=True))
    op.add_column("packing_items", sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("packing_items", "is_completed", server_default=None)


def downgrade() -> None:
    op.drop_column("packing_items", "is_completed")
    op.drop_column("packing_items", "assigned_to")
