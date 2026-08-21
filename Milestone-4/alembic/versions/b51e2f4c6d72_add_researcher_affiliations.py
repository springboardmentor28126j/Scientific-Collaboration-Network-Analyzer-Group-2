"""add researcher affiliations

Revision ID: b51e2f4c6d72
Revises: a74e3e9012c0
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b51e2f4c6d72"
down_revision: str | Sequence[str] | None = "a74e3e9012c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "researcher_profiles",
        sa.Column("affiliations", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )


def downgrade() -> None:
    op.drop_column("researcher_profiles", "affiliations")
