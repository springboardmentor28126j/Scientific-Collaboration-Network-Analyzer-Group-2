"""merge password_reset and collaboration_module heads

Revision ID: 17b43b014d35
Revises: c2d3e4f5a6b7, m1n2o3p4q5r6
Create Date: 2026-07-29 21:30:14.844030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17b43b014d35'
down_revision: Union[str, None] = ('c2d3e4f5a6b7', 'm1n2o3p4q5r6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
