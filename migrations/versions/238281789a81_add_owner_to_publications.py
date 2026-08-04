"""Add owner to publications

Revision ID: 238281789a81
Revises: 68a2277b8a77
Create Date: 2026-07-16 16:37:15.464235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '238281789a81'
down_revision: Union[str, Sequence[str], None] = '68a2277b8a77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "publications",
        sa.Column("owner_id", sa.UUID(), nullable=True)
    )

    op.create_foreign_key(
        "fk_publications_owner",
        "publications",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_publications_owner",
        "publications",
        type_="foreignkey",
    )

    op.drop_column(
        "publications",
        "owner_id",
    )

    # ### end Alembic commands ###
