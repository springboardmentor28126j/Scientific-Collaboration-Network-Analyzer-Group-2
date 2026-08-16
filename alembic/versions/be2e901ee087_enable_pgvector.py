"""enable pgvector

Revision ID: be2e901ee087
Revises: 526ca2a928eb
Create Date: 2026-08-16 03:54:30.850781

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "be2e901ee087"
down_revision: str | None = "526ca2a928eb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
