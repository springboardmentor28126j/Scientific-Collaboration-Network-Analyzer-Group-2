"""add mfa_enabled and mfa_otp token type

Revision ID: 0021_mfa_otp
Revises: 0020_messaging
Create Date: 2026-08-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0021_mfa_otp"
down_revision = "0020_messaging"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute("ALTER TYPE authtokentype ADD VALUE IF NOT EXISTS 'mfa_otp'")


def downgrade() -> None:
    op.drop_column("users", "mfa_enabled")
    # Postgres doesn't support removing enum values — no-op on downgrade.