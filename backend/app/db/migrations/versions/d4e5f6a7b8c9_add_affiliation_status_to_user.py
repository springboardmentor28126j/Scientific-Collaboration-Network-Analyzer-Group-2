"""add affiliation_status to user

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


affiliation_status_enum = sa.Enum(
    'NOT_APPLICABLE', 'PENDING', 'APPROVED', 'REJECTED', name='affiliationstatus'
)


def upgrade() -> None:
    affiliation_status_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'user',
        sa.Column(
            'affiliation_status', affiliation_status_enum, nullable=False, server_default='NOT_APPLICABLE'
        ),
    )
    # Backfill: any existing researcher who already has an institution_id was
    # implicitly trusted before this workflow existed -- treat them as approved
    # rather than retroactively putting the whole existing roster in a pending
    # queue.
    op.execute(
        "UPDATE \"user\" SET affiliation_status = 'APPROVED' "
        "WHERE role = 'RESEARCHER' AND institution_id IS NOT NULL"
    )
    op.execute(
        "UPDATE \"user\" SET affiliation_status = 'APPROVED' "
        "WHERE role IN ('INSTITUTION_ADMIN', 'REVIEWER') AND institution_id IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_column('user', 'affiliation_status')
    affiliation_status_enum.drop(op.get_bind(), checkfirst=True)
