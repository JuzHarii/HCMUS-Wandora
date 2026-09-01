"""add user password hash

Revision ID: f90ac4e2d112
Revises: d12d8d56c900
Create Date: 2026-08-13 19:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f90ac4e2d112"
down_revision: Union[str, Sequence[str], None] = "d12d8d56c900"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("password_hash", sa.String(length=255), nullable=False, server_default=""))
        batch_op.alter_column("password_hash", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "password_hash")
