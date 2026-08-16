"""add email_verification_token table

Revision ID: f1a2b3c4d5e6
Revises: d5d4e515df7b
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'd5d4e515df7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'email_verification_token',
        sa.Column('token_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_email_verification_token_token'), 'email_verification_token', ['token'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_email_verification_token_token'), table_name='email_verification_token')
    op.drop_table('email_verification_token')
