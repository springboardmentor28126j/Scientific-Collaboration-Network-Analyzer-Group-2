"""publications: add publications and publication_authors tables

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
    op.create_table(
        "publications",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("venue", sa.String(255), nullable=True),
        sa.Column("doi_link", sa.String(500), nullable=True),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "publication_authors",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "publication_id",
            sa.Integer(),
            sa.ForeignKey("publications.id"),
            nullable=False,
        ),
        sa.Column(
            "researcher_id",
            sa.Integer(),
            sa.ForeignKey("researchers.id"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "publication_id", "researcher_id", name="uq_publication_researcher"
        ),
    )


def downgrade() -> None:
    op.drop_table("publication_authors")
    op.drop_table("publications")
