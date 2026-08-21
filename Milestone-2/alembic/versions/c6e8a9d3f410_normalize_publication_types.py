"""normalize legacy publication type values

Revision ID: c6e8a9d3f410
Revises: b51e2f4c6d72
"""

from collections.abc import Sequence

from alembic import op

revision: str = "c6e8a9d3f410"
down_revision: str | Sequence[str] | None = "b51e2f4c6d72"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("UPDATE publications SET publication_type = 'JOURNAL' WHERE publication_type = 'JOURNAL_PAPER'")
    op.execute("UPDATE publications SET publication_type = 'CONFERENCE' WHERE publication_type = 'CONFERENCE_PAPER'")
    op.execute("UPDATE publications SET publication_type = 'BOOK' WHERE publication_type = 'BOOK_CHAPTER'")


def downgrade() -> None:
    op.execute("UPDATE publications SET publication_type = 'JOURNAL_PAPER' WHERE publication_type = 'JOURNAL'")
    op.execute("UPDATE publications SET publication_type = 'CONFERENCE_PAPER' WHERE publication_type = 'CONFERENCE'")
    op.execute("UPDATE publications SET publication_type = 'BOOK_CHAPTER' WHERE publication_type = 'BOOK'")
