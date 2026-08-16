"""add project invite/accept flow and project group chat

Revision ID: p4q5r6s7t8u9
Revises: o3p4q5r6s7t8
Create Date: 2026-08-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'p4q5r6s7t8u9'
down_revision: Union[str, None] = 'o3p4q5r6s7t8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


member_status_enum = postgresql.ENUM('PENDING', 'ACCEPTED', 'DECLINED', name='projectmemberstatus')
member_status_col = postgresql.ENUM('PENDING', 'ACCEPTED', 'DECLINED', name='projectmemberstatus', create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    member_status_enum.create(bind, checkfirst=True)

    # server_default='ACCEPTED' backfills every existing project_member row
    # as an active member -- nobody already on a project gets bumped back
    # to "pending" by this migration.
    op.add_column(
        'project_member',
        sa.Column('status', member_status_col, nullable=False, server_default='ACCEPTED'),
    )
    op.add_column('project_member', sa.Column('invited_by_id', sa.Integer(), nullable=True))
    op.add_column('project_member', sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        'fk_project_member_invited_by', 'project_member', 'researcher_profile',
        ['invited_by_id'], ['researcher_id'], ondelete='SET NULL',
    )
    op.create_index('ix_project_member_status', 'project_member', ['status'])

    op.create_table(
        'project_message',
        sa.Column('project_message_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.project_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['researcher_profile.researcher_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_message_id'),
    )
    op.create_index('ix_project_message_project_created', 'project_message', ['project_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_project_message_project_created', table_name='project_message')
    op.drop_table('project_message')

    op.drop_index('ix_project_member_status', table_name='project_member')
    op.drop_constraint('fk_project_member_invited_by', 'project_member', type_='foreignkey')
    op.drop_column('project_member', 'responded_at')
    op.drop_column('project_member', 'invited_by_id')
    op.drop_column('project_member', 'status')

    member_status_enum.drop(op.get_bind(), checkfirst=True)