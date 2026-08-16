"""add collaboration_request, collaboration, and collaboration_publication tables

Revision ID: m1n2o3p4q5r6
Revises: g1h2i3j4k5l6
Create Date: 2026-07-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'm1n2o3p4q5r6'
down_revision: Union[str, None] = 'g1h2i3j4k5l6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


request_status_enum = postgresql.ENUM(
    'PENDING', 'ACCEPTED', 'REJECTED', 'CANCELLED', name='collaborationrequeststatus'
)
request_status_col = postgresql.ENUM(
    'PENDING', 'ACCEPTED', 'REJECTED', 'CANCELLED', name='collaborationrequeststatus', create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    request_status_enum.create(bind, checkfirst=True)

    op.create_table(
        'collaboration_request',
        sa.Column('collaboration_request_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('requester_id', sa.Integer(), nullable=False),
        sa.Column('addressee_id', sa.Integer(), nullable=False),
        sa.Column('status', request_status_col, nullable=False, server_default='PENDING'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['requester_id'], ['researcher_profile.researcher_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['addressee_id'], ['researcher_profile.researcher_id'], ondelete='CASCADE'),
        sa.CheckConstraint('requester_id != addressee_id', name='ck_collaboration_request_not_self'),
    )
    op.create_index('ix_collaboration_request_requester_id', 'collaboration_request', ['requester_id'])
    op.create_index('ix_collaboration_request_addressee_id', 'collaboration_request', ['addressee_id'])
    op.create_index('ix_collaboration_request_status', 'collaboration_request', ['status'])

    op.create_table(
        'collaboration',
        sa.Column('collaboration_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('researcher1_id', sa.Integer(), nullable=False),
        sa.Column('researcher2_id', sa.Integer(), nullable=False),
        sa.Column('strength', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('first_collaboration', sa.Date(), nullable=True),
        sa.Column('last_collaboration', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['researcher1_id'], ['researcher_profile.researcher_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['researcher2_id'], ['researcher_profile.researcher_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('researcher1_id', 'researcher2_id', name='uq_collaboration_pair'),
        sa.CheckConstraint('researcher1_id < researcher2_id', name='ck_collaboration_ordered_pair'),
    )
    op.create_index('ix_collaboration_researcher1_id', 'collaboration', ['researcher1_id'])
    op.create_index('ix_collaboration_researcher2_id', 'collaboration', ['researcher2_id'])

    op.create_table(
        'collaboration_publication',
        sa.Column('collaboration_publication_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('collaboration_id', sa.Integer(), nullable=False),
        sa.Column('publication_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['collaboration_id'], ['collaboration.collaboration_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['publication_id'], ['publication.publication_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('collaboration_id', 'publication_id', name='uq_collaboration_publication'),
    )
    op.create_index('ix_collaboration_publication_collaboration_id', 'collaboration_publication', ['collaboration_id'])
    op.create_index('ix_collaboration_publication_publication_id', 'collaboration_publication', ['publication_id'])


def downgrade() -> None:
    op.drop_index('ix_collaboration_publication_publication_id', table_name='collaboration_publication')
    op.drop_index('ix_collaboration_publication_collaboration_id', table_name='collaboration_publication')
    op.drop_table('collaboration_publication')

    op.drop_index('ix_collaboration_researcher2_id', table_name='collaboration')
    op.drop_index('ix_collaboration_researcher1_id', table_name='collaboration')
    op.drop_table('collaboration')

    op.drop_index('ix_collaboration_request_status', table_name='collaboration_request')
    op.drop_index('ix_collaboration_request_addressee_id', table_name='collaboration_request')
    op.drop_index('ix_collaboration_request_requester_id', table_name='collaboration_request')
    op.drop_table('collaboration_request')

    request_status_enum.drop(op.get_bind(), checkfirst=True)
