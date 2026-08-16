"""add project and project_member tables

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-07-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


status_enum = postgresql.ENUM('PLANNED', 'ONGOING', 'COMPLETED', 'CANCELLED', name='projectstatus')
status_col = postgresql.ENUM('PLANNED', 'ONGOING', 'COMPLETED', 'CANCELLED', name='projectstatus', create_type=False)
member_role_enum = postgresql.ENUM('LEAD', 'MEMBER', name='projectmemberrole')
member_role_col = postgresql.ENUM('LEAD', 'MEMBER', name='projectmemberrole', create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    status_enum.create(bind, checkfirst=True)
    member_role_enum.create(bind, checkfirst=True)

    op.create_table(
        'project',
        sa.Column('project_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', status_col, nullable=False, server_default='PLANNED'),
        sa.Column('lead_researcher_id', sa.Integer(), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['lead_researcher_id'], ['researcher_profile.researcher_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['institution_id'], ['institution.institution_id'], ondelete='SET NULL'),
    )

    op.create_table(
        'project_member',
        sa.Column('project_member_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('researcher_id', sa.Integer(), nullable=False),
        sa.Column('role', member_role_col, nullable=False, server_default='MEMBER'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.project_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['researcher_id'], ['researcher_profile.researcher_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('project_id', 'researcher_id', name='uq_project_member'),
    )
    op.create_index('ix_project_member_project_id', 'project_member', ['project_id'])
    op.create_index('ix_project_member_researcher_id', 'project_member', ['researcher_id'])


def downgrade() -> None:
    op.drop_index('ix_project_member_researcher_id', table_name='project_member')
    op.drop_index('ix_project_member_project_id', table_name='project_member')
    op.drop_table('project_member')
    op.drop_table('project')
    member_role_enum.drop(op.get_bind(), checkfirst=True)
    status_enum.drop(op.get_bind(), checkfirst=True)
