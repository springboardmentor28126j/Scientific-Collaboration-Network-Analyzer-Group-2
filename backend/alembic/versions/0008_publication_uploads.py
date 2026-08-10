"""publications: add file upload columns

Revision ID: 0008_publication_uploads
Revises: 0007_publications
Create Date: 2026-07-22

"""
from alembic import op
import sqlalchemy as sa

revision = "0008_publication_uploads"
down_revision = "0007_publications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "publications", sa.Column("stored_filename", sa.String(255), nullable=True)
    )
    op.add_column(
        "publications", sa.Column("original_filename", sa.String(255), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("publications", "original_filename")
    op.drop_column("publications", "stored_filename")
