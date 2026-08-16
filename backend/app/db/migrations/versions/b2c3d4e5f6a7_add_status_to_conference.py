"""add status to conference

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    postgresql.ENUM(
        'PLANNED', 'REGISTRATION_OPEN', 'ONGOING', 'COMPLETED', 'CANCELLED',
        name='conferencestatus',
    ).create(bind, checkfirst=True)

    # create_type=False -- the type was just created above; add_column would
    # otherwise try to create it again and fail with "already exists".
    status_col = postgresql.ENUM(
        'PLANNED', 'REGISTRATION_OPEN', 'ONGOING', 'COMPLETED', 'CANCELLED',
        name='conferencestatus', create_type=False,
    )

    op.add_column(
        'conference',
        sa.Column('status', status_col, nullable=False, server_default='PLANNED'),
    )


def downgrade() -> None:
    op.drop_column('conference', 'status')
    postgresql.ENUM(name='conferencestatus').drop(op.get_bind(), checkfirst=True)