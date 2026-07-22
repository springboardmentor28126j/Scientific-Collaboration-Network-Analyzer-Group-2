"""add publication, publication_author, conference, conference_participation tables

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-07-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # --- create the Postgres ENUM types explicitly, once ---
    postgresql.ENUM(
        'JOURNAL_PAPER', 'CONFERENCE_PAPER', 'BOOK', 'PATENT', 'TECHNICAL_REPORT', 'OTHER',
        name='publicationtype',
    ).create(bind, checkfirst=True)

    postgresql.ENUM(
        'DRAFT', 'SUBMITTED', 'PUBLISHED', 'ARCHIVED', name='publicationstatus'
    ).create(bind, checkfirst=True)

    postgresql.ENUM(
        'ATTENDEE', 'PRESENTER', 'ORGANIZER', 'REVIEWER', name='participationrole'
    ).create(bind, checkfirst=True)

    postgresql.ENUM(
        'DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'ACCEPTED', 'REJECTED', 'PUBLISHED', name='submissionstatus'
    ).create(bind, checkfirst=True)

    # --- IMPORTANT: create_type=False below ---
    # These ENUM objects reference the types we JUST created above. Without
    # create_type=False, SQLAlchemy tries to auto-create the type a SECOND
    # time as part of create_table(), which fails with "already exists".
    publication_type_col = postgresql.ENUM(
        'JOURNAL_PAPER', 'CONFERENCE_PAPER', 'BOOK', 'PATENT', 'TECHNICAL_REPORT', 'OTHER',
        name='publicationtype', create_type=False,
    )
    publication_status_col = postgresql.ENUM(
        'DRAFT', 'SUBMITTED', 'PUBLISHED', 'ARCHIVED', name='publicationstatus', create_type=False,
    )
    participation_role_col = postgresql.ENUM(
        'ATTENDEE', 'PRESENTER', 'ORGANIZER', 'REVIEWER', name='participationrole', create_type=False,
    )
    submission_status_col = postgresql.ENUM(
        'DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'ACCEPTED', 'REJECTED', 'PUBLISHED',
        name='submissionstatus', create_type=False,
    )

    # --- publication ---
    op.create_table(
        'publication',
        sa.Column('publication_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('publication_type', publication_type_col, nullable=False),
        sa.Column('status', publication_status_col, nullable=False, server_default='DRAFT'),
        sa.Column('primary_author_id', sa.Integer(),
                  sa.ForeignKey('researcher_profile.researcher_id', ondelete='CASCADE'), nullable=False),
        sa.Column('institution_id', sa.Integer(),
                  sa.ForeignKey('institution.institution_id', ondelete='SET NULL'), nullable=True),
        sa.Column('venue_name', sa.String(length=300), nullable=True),
        sa.Column('doi', sa.String(length=150), nullable=True),
        sa.Column('publication_date', sa.Date(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_publication_doi', 'publication', ['doi'], unique=True)

    # --- publication_author ---
    op.create_table(
        'publication_author',
        sa.Column('publication_author_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('publication_id', sa.Integer(),
                  sa.ForeignKey('publication.publication_id', ondelete='CASCADE'), nullable=False),
        sa.Column('researcher_id', sa.Integer(),
                  sa.ForeignKey('researcher_profile.researcher_id', ondelete='CASCADE'), nullable=False),
        sa.Column('author_order', sa.Integer(), nullable=False, server_default='1'),
        sa.UniqueConstraint('publication_id', 'researcher_id', name='uq_publication_author'),
    )

    # --- conference ---
    op.create_table(
        'conference',
        sa.Column('conference_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('location', sa.String(length=300), nullable=True),
        sa.Column('organizing_institution_id', sa.Integer(),
                  sa.ForeignKey('institution.institution_id', ondelete='SET NULL'), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- conference_participation ---
    op.create_table(
        'conference_participation',
        sa.Column('participation_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('conference_id', sa.Integer(),
                  sa.ForeignKey('conference.conference_id', ondelete='CASCADE'), nullable=False),
        sa.Column('researcher_id', sa.Integer(),
                  sa.ForeignKey('researcher_profile.researcher_id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', participation_role_col, nullable=False),
        sa.Column('submission_status', submission_status_col, nullable=False, server_default='DRAFT'),
        sa.Column('presentation_title', sa.String(length=500), nullable=True),
        sa.Column('publication_id', sa.Integer(),
                  sa.ForeignKey('publication.publication_id', ondelete='SET NULL'), nullable=True),
        sa.Column('registered_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('conference_id', 'researcher_id', name='uq_conference_researcher'),
    )


def downgrade() -> None:
    op.drop_table('conference_participation')
    op.drop_table('conference')
    op.drop_table('publication_author')
    op.drop_index('ix_publication_doi', table_name='publication')
    op.drop_table('publication')

    bind = op.get_bind()
    postgresql.ENUM(name='submissionstatus').drop(bind, checkfirst=True)
    postgresql.ENUM(name='participationrole').drop(bind, checkfirst=True)
    postgresql.ENUM(name='publicationstatus').drop(bind, checkfirst=True)
    postgresql.ENUM(name='publicationtype').drop(bind, checkfirst=True)