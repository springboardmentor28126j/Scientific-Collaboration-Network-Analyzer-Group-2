"""create collaborations table

Revision ID: 3b37878047c4
Revises: 893a0c6dc859
Create Date: 2026-08-04 13:43:55.442000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b37878047c4'
down_revision: Union[str, Sequence[str], None] = '893a0c6dc859'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "collaborations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("sender_id", sa.UUID(), nullable=False),
        sa.Column("receiver_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["receiver_id"],
            ["users.id"]
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_table("collaborations")
    # ### end Alembic commands ###
