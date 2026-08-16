"""add citation table

Revision ID: n2o3p4q5r6s7
Revises: 17b43b014d35
Create Date: 2026-08-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'n2o3p4q5r6s7'
down_revision: Union[str, None] = '17b43b014d35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'citation',
        sa.Column('citation_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('citing_publication_id', sa.Integer(), nullable=False),
        sa.Column('cited_publication_id', sa.Integer(), nullable=True),
        sa.Column('external_title', sa.String(length=500), nullable=True),
        sa.Column('external_authors', sa.String(length=500), nullable=True),
        sa.Column('external_venue', sa.String(length=300), nullable=True),
        sa.Column('external_year', sa.Integer(), nullable=True),
        sa.Column('external_doi', sa.String(length=150), nullable=True),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('added_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['citing_publication_id'], ['publication.publication_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cited_publication_id'], ['publication.publication_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['added_by_id'], ['researcher_profile.researcher_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('citation_id'),
        sa.CheckConstraint('cited_publication_id IS NOT NULL OR external_title IS NOT NULL', name='ck_citation_has_target'),
        sa.CheckConstraint('citing_publication_id != cited_publication_id', name='ck_citation_not_self'),
        sa.UniqueConstraint('citing_publication_id', 'cited_publication_id', name='uq_citation_internal_pair'),
    )
    op.create_index(op.f('ix_citation_citing_publication_id'), 'citation', ['citing_publication_id'])
    op.create_index(op.f('ix_citation_cited_publication_id'), 'citation', ['cited_publication_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_citation_cited_publication_id'), table_name='citation')
    op.drop_index(op.f('ix_citation_citing_publication_id'), table_name='citation')
    op.drop_table('citation')