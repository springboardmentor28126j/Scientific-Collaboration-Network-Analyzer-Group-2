"""publications: add type column (journal/conference/book/patent/report)

Revision ID: 0010_publication_type
Revises: 0009_publication_status
Create Date: 2026-07-23

"""
from alembic import op
import sqlalchemy as sa

revision = "0010_publication_type"
down_revision = "0009_publication_status"
branch_labels = None
depends_on = None


def upgrade() -> None:
    publication_type = sa.Enum(
        "journal_paper", "conference_paper", "book", "patent", "technical_report",
        name="publicationtype",
    )
    publication_type.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "publications",
        sa.Column("type", publication_type, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("publications", "type")
    sa.Enum(name="publicationtype").drop(op.get_bind(), checkfirst=True)
    