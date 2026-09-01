"""add_pa4_extra_tables_and_columns

Revision ID: 60c3c9c4dae5
Revises: e5f0a1b2c3d4
Create Date: 2026-08-28 16:06:44.673898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60c3c9c4dae5'
down_revision: Union[str, Sequence[str], None] = 'e5f0a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'place_reviews',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('place_name', sa.String(length=255), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id', 'user_id', 'place_name', name='uq_place_reviews_workspace_user_place')
    )
    op.create_table(
        'packing_list_entries',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('packing_item_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('is_checked', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['packing_item_id'], ['packing_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'activity_comments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('activity_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['itinerary_activities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('activity_comments', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_activity_comments_activity_id'), ['activity_id'], unique=False)

    op.create_table(
        'activity_votes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('activity_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('vote_value', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['itinerary_activities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('activity_id', 'user_id', name='uq_activity_user_vote')
    )
    with op.batch_alter_table('activity_votes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_activity_votes_activity_id'), ['activity_id'], unique=False)

    with op.batch_alter_table('chat_messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sender_role', sa.String(length=50), nullable=False, server_default="user"))

    with op.batch_alter_table('invite_tokens', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_invite_tokens_token'), ['token'], unique=True)

    with op.batch_alter_table('itinerary_activities', schema=None) as batch_op:
        batch_op.add_column(sa.Column('order_index', sa.Integer(), nullable=False, server_default="0"))
        batch_op.alter_column('external_url', existing_type=sa.VARCHAR(length=500), type_=sa.String(length=1000), existing_nullable=True)
        batch_op.alter_column('created_at', existing_type=sa.DATETIME(), nullable=True)

    with op.batch_alter_table('itinerary_days', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', sa.Date(), nullable=True))
        batch_op.alter_column('title', existing_type=sa.VARCHAR(length=255), nullable=True)
        batch_op.create_unique_constraint('uq_itinerary_days_workspace_day_index', ['workspace_id', 'day_index'])

    with op.batch_alter_table('locations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('workspace_id', sa.String(length=36), nullable=False, server_default=""))
        batch_op.add_column(sa.Column('note', sa.Text(), nullable=True))

    with op.batch_alter_table('packing_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('is_shared', sa.Boolean(), nullable=False, server_default=sa.text('0')))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hashed_password', sa.String(length=255), nullable=True))
        batch_op.alter_column('full_name', existing_type=sa.VARCHAR(length=255), nullable=True)
        batch_op.alter_column('password_hash', existing_type=sa.VARCHAR(length=255), nullable=True)

    with op.batch_alter_table('workspace_destinations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('country', sa.String(length=255), nullable=True))
        batch_op.alter_column('destination_name', existing_type=sa.VARCHAR(length=255), nullable=True)

    with op.batch_alter_table('workspace_members', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(length=50), nullable=False, server_default="member"))
        batch_op.add_column(sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False))

    with op.batch_alter_table('workspaces', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('preferences_json', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('history_snapshots', sa.Text(), nullable=True))
        batch_op.alter_column('destination', existing_type=sa.VARCHAR(length=255), nullable=True)
        batch_op.alter_column('status', existing_type=sa.VARCHAR(length=32), type_=sa.String(length=50), existing_nullable=False)
        batch_op.alter_column('itinerary_source', existing_type=sa.VARCHAR(length=32), type_=sa.String(length=50), existing_nullable=True)
        batch_op.alter_column('updated_at', existing_type=sa.DATETIME(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('workspaces', schema=None) as batch_op:
        batch_op.drop_column('history_snapshots')
        batch_op.drop_column('preferences_json')
        batch_op.drop_column('owner_id')

    with op.batch_alter_table('workspace_members', schema=None) as batch_op:
        batch_op.drop_column('joined_at')
        batch_op.drop_column('role')

    with op.batch_alter_table('workspace_destinations', schema=None) as batch_op:
        batch_op.drop_column('country')
        batch_op.drop_column('name')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('hashed_password')

    with op.batch_alter_table('packing_items', schema=None) as batch_op:
        batch_op.drop_column('is_shared')
        batch_op.drop_column('category')

    with op.batch_alter_table('locations', schema=None) as batch_op:
        batch_op.drop_column('note')
        batch_op.drop_column('workspace_id')

    with op.batch_alter_table('itinerary_days', schema=None) as batch_op:
        batch_op.drop_constraint('uq_itinerary_days_workspace_day_index', type_='unique')
        batch_op.drop_column('date')

    with op.batch_alter_table('itinerary_activities', schema=None) as batch_op:
        batch_op.drop_column('order_index')

    with op.batch_alter_table('invite_tokens', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_invite_tokens_token'))

    with op.batch_alter_table('chat_messages', schema=None) as batch_op:
        batch_op.drop_column('sender_role')

    with op.batch_alter_table('activity_votes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_activity_votes_activity_id'))

    op.drop_table('activity_votes')
    with op.batch_alter_table('activity_comments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_activity_comments_activity_id'))

    op.drop_table('activity_comments')
    op.drop_table('packing_list_entries')
    op.drop_table('place_reviews')
