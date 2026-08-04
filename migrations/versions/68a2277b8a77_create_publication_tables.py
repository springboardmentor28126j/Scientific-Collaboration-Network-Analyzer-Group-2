"""create publication tables

Revision ID: 68a2277b8a77
Revises: d823056371d4
Create Date: 2026-07-16 15:25:37.843970

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68a2277b8a77'
down_revision: Union[str, Sequence[str], None] = 'd823056371d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "publications",

        sa.Column("id", sa.UUID(), primary_key=True),

        sa.Column("title", sa.String(500), nullable=False),

        sa.Column("abstract", sa.Text()),

        sa.Column("doi", sa.String(255)),

        sa.Column("journal", sa.String(255)),

        sa.Column("conference", sa.String(255)),

        sa.Column("publication_year", sa.Integer(), nullable=False),

        sa.Column(
            "publication_type",
            sa.Enum(
                "JOURNAL",
                "CONFERENCE",
                "BOOK",
                "BOOK_CHAPTER",
                "PATENT",
                "THESIS",
                name="publicationtype"
            ),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "SUBMITTED",
                "ACCEPTED",
                "PUBLISHED",
                "REJECTED",
                name="publicationstatus"
            ),
            nullable=False,
        ),

        sa.Column("url", sa.String(500)),

        sa.Column("citation_count", sa.Integer(), server_default="0"),

        sa.Column("file_name", sa.String(255)),

        sa.Column("file_path", sa.String(500)),

        sa.Column("file_size", sa.Integer()),

        sa.Column("file_type", sa.String(100)),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint("doi"),

        sa.CheckConstraint(
            "citation_count >= 0",
            name="ck_citation_count_positive",
        ),
    )


    op.create_table(

        "publication_authors",

        sa.Column(
            "publication_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "researcher_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "author_order",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),

        sa.Column(
            "is_corresponding_author",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),

        sa.ForeignKeyConstraint(
            ["publication_id"],
            ["publications.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["researcher_id"],
            ["researchers.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "publication_id",
            "researcher_id",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("publication_authors")

    op.drop_table("publications")
