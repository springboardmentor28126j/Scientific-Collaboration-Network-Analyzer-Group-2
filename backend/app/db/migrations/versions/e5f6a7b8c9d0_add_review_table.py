"""add review table

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


target_type_enum = postgresql.ENUM('PUBLICATION', 'CONFERENCE_SUBMISSION', name='reviewtargettype')
target_type_col = postgresql.ENUM('PUBLICATION', 'CONFERENCE_SUBMISSION', name='reviewtargettype', create_type=False)
status_enum = postgresql.ENUM('ASSIGNED', 'ACCEPTED', 'DECLINED', 'COMPLETED', name='reviewstatus')
status_col = postgresql.ENUM('ASSIGNED', 'ACCEPTED', 'DECLINED', 'COMPLETED', name='reviewstatus', create_type=False)
recommendation_enum = postgresql.ENUM(
    'ACCEPT', 'MINOR_REVISION', 'MAJOR_REVISION', 'REJECT', name='reviewrecommendation'
)
recommendation_col = postgresql.ENUM(
    'ACCEPT', 'MINOR_REVISION', 'MAJOR_REVISION', 'REJECT', name='reviewrecommendation', create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    target_type_enum.create(bind, checkfirst=True)
    status_enum.create(bind, checkfirst=True)
    recommendation_enum.create(bind, checkfirst=True)

    op.create_table(
        'review',
        sa.Column('review_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('target_type', target_type_col, nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('assigned_by', sa.Integer(), nullable=True),
        sa.Column('status', status_col, nullable=False, server_default='ASSIGNED'),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('recommendation', recommendation_col, nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['reviewer_id'], ['user.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['user.user_id'], ondelete='SET NULL'),
    )
    op.create_index('ix_review_reviewer_id', 'review', ['reviewer_id'])
    op.create_index('ix_review_target', 'review', ['target_type', 'target_id'])


def downgrade() -> None:
    op.drop_index('ix_review_target', table_name='review')
    op.drop_index('ix_review_reviewer_id', table_name='review')
    op.drop_table('review')
    recommendation_enum.drop(op.get_bind(), checkfirst=True)
    status_enum.drop(op.get_bind(), checkfirst=True)
    target_type_enum.drop(op.get_bind(), checkfirst=True)
