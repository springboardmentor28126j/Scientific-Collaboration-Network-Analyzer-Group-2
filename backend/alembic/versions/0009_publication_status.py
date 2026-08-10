"""publications: add status column (Draft/Submitted/Published/Archived)

Revision ID: 0009_publication_status
Revises: 0008_publication_uploads
Create Date: 2026-07-22

"""
from alembic import op
import sqlalchemy as sa

revision = "0009_publication_status"
down_revision = "0008_publication_uploads"
branch_labels = None
depends_on = None

publication_status_enum = sa.Enum(
    "draft", "submitted", "published", "archived", name="publicationstatus"
)


def upgrade() -> None:
    publication_status_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "publications",
        sa.Column(
            "status",
            publication_status_enum,
            nullable=False,
            server_default="draft",
        ),
    )


def downgrade() -> None:
    op.drop_column("publications", "status")
    publication_status_enum.drop(op.get_bind(), checkfirst=True)
