"""add conference table

Revision ID: b7e7b16bcfea
Revises: fecc1ecc3773
Create Date: 2026-07-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b7e7b16bcfea"
down_revision: Union[str, Sequence[str], None] = "fecc1ecc3773"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "conferences",

        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "location",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "conference_date",
            sa.Date(),
            nullable=True,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:

    op.drop_table("conferences")
