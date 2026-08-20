"""Merge trip into workspace, add status, owner, comments, and votes

Revision ID: 23814480187d
Revises: '47178f266333'
Create Date: 2026-08-20 10:48:05.657436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23814480187d'
down_revision: Union[str, None] = '47178f266333'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    op.execute("DROP TABLE IF EXISTS trips")

    # Add hashed_password if not exists
    user_cols = [c["name"] for c in inspector.get_columns("users")]
    if "hashed_password" not in user_cols:
        with op.batch_alter_table("users", schema=None) as batch_op:
            batch_op.add_column(sa.Column("hashed_password", sa.String(length=255), nullable=True))

    # Add workspace cols if not exist
    ws_cols = [c["name"] for c in inspector.get_columns("workspaces")]
    with op.batch_alter_table("workspaces", schema=None) as batch_op:
        if "owner_id" not in ws_cols:
            batch_op.add_column(sa.Column("owner_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key("fk_workspaces_owner_id_users", "users", ["owner_id"], ["id"], ondelete="CASCADE")
        if "status" not in ws_cols:
            batch_op.add_column(sa.Column("status", sa.String(length=50), nullable=False, server_default="Draft"))
        if "history_snapshots" not in ws_cols:
            batch_op.add_column(sa.Column("history_snapshots", sa.Text(), nullable=True))

    tables = inspector.get_table_names()
    if "activity_comments" not in tables:
        op.create_table(
            'activity_comments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('activity_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.ForeignKeyConstraint(['activity_id'], ['itinerary_activities.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_activity_comments_id', 'activity_comments', ['id'], unique=False)
        op.create_index('ix_activity_comments_activity_id', 'activity_comments', ['activity_id'], unique=False)

    if "activity_votes" not in tables:
        op.create_table(
            'activity_votes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('activity_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('vote_value', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.ForeignKeyConstraint(['activity_id'], ['itinerary_activities.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('activity_id', 'user_id', name='uq_activity_user_vote')
        )
        op.create_index('ix_activity_votes_id', 'activity_votes', ['id'], unique=False)
        op.create_index('ix_activity_votes_activity_id', 'activity_votes', ['activity_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_activity_votes_activity_id', table_name='activity_votes')
    op.drop_index('ix_activity_votes_id', table_name='activity_votes')
    op.drop_table('activity_votes')

    op.drop_index('ix_activity_comments_activity_id', table_name='activity_comments')
    op.drop_index('ix_activity_comments_id', table_name='activity_comments')
    op.drop_table('activity_comments')

    with op.batch_alter_table('workspaces', schema=None) as batch_op:
        batch_op.drop_constraint('fk_workspaces_owner_id_users', type_='foreignkey')
        batch_op.drop_column('history_snapshots')
        batch_op.drop_column('status')
        batch_op.drop_column('owner_id')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('hashed_password')
