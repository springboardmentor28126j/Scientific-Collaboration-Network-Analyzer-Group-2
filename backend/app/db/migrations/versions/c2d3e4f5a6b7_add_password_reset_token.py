"""add password_reset_token table

Revision ID: c2d3e4f5a6b7
Revises: m1n2o3p4q5r6
Create Date: 2026-07-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c2d3e4f5a6b7'
down_revision: Union[str, None] = 'm1n2o3p4q5r6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'password_reset_token',
        sa.Column('token_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_password_reset_token_token'), 'password_reset_token', ['token'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_password_reset_token_token'), table_name='password_reset_token')
    op.drop_table('password_reset_token')