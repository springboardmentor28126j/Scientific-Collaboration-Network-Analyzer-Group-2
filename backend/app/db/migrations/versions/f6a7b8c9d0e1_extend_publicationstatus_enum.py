"""extend publicationstatus enum with under_review and accepted

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-07-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ALTER TYPE ... ADD VALUE cannot run inside the transaction Alembic
    # normally wraps each migration in, so we close it out first.
    op.execute("COMMIT")
    op.execute("ALTER TYPE publicationstatus ADD VALUE IF NOT EXISTS 'UNDER_REVIEW'")
    op.execute("ALTER TYPE publicationstatus ADD VALUE IF NOT EXISTS 'ACCEPTED'")


def downgrade() -> None:
    # Postgres has no ALTER TYPE ... DROP VALUE. Downgrading this enum
    # cleanly would mean rebuilding the type and the column that uses it;
    # since UNDER_REVIEW/ACCEPTED are additive and non-breaking, we leave
    # them in place on downgrade rather than risk data loss on a rebuild.
    pass
