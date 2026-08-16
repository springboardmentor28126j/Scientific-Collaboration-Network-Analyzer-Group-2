"""add system_setting table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'system_setting',
        sa.Column('setting_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('key', sa.String(length=150), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['updated_by'], ['user.user_id'], ondelete='SET NULL'),
    )
    op.create_unique_constraint('uq_system_setting_key', 'system_setting', ['key'])
    op.create_index('ix_system_setting_key', 'system_setting', ['key'])


def downgrade() -> None:
    op.drop_index('ix_system_setting_key', table_name='system_setting')
    op.drop_constraint('uq_system_setting_key', 'system_setting', type_='unique')
    op.drop_table('system_setting')
