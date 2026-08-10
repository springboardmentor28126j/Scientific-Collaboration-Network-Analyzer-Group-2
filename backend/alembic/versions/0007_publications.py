"""publications: add publications and publication_authors tables

Revision ID: 0007_publications
Revises: 0006_institution_details
Create Date: 2026-07-22

NOTE (adapted for this project): unlike the upstream reference this
migration was ported from, this project's own 0002_milestone2 migration
already created the `publications` and `publication_authors` tables
(they were built ahead of this teammate's branch). Re-creating them here
would fail against this project's DB, so upgrade()/downgrade() are
no-ops -- this revision exists purely to keep the migration chain's
revision IDs lined up with 0008-0012, which do depend on it.
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_publications"
down_revision = "0006_institution_details"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: publications / publication_authors already exist (see note above).
    pass


def downgrade() -> None:
    # No-op to match upgrade(); the tables predate this revision in this project.
    pass
