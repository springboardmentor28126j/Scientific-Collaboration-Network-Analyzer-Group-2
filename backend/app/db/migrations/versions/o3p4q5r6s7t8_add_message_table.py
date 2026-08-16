"""add message table

Revision ID: o3p4q5r6s7t8
Revises: n2o3p4q5r6s7
Create Date: 2026-08-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'o3p4q5r6s7t8'
down_revision: Union[str, None] = 'n2o3p4q5r6s7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'message',
        sa.Column('message_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('collaboration_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['collaboration_id'], ['collaboration.collaboration_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['researcher_profile.researcher_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('message_id'),
    )
    op.create_index('ix_message_collaboration_created', 'message', ['collaboration_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_message_collaboration_created', table_name='message')
    op.drop_table('message')