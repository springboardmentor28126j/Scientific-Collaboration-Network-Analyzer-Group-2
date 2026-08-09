"""publications: (tables already created in 0002_milestone2 — this is now a no-op, kept for revision-chain continuity)

Revision ID: 0007_publications
Revises: 0006_institution_details
Create Date: 2026-07-22

"""
from alembic import op
import sqlalchemy as sa

revision = "0007_publications"
down_revision = "0006_institution_details"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass