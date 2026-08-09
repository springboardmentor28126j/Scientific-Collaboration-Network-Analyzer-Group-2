"""google sign-in support: nullable password_hash, google_sub column

Revision ID: 0019_google_signin
Revises: 0018_auth_audit
Create Date: 2026-08-06

"""
from alembic import op
import sqlalchemy as sa

revision = "0019_google_signin"
down_revision = "0018_auth_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("users", "password_hash", existing_type=sa.String(length=255), nullable=True)
    op.add_column("users", sa.Column("google_sub", sa.String(length=255), nullable=True))
    op.create_unique_constraint("uq_users_google_sub", "users", ["google_sub"])


def downgrade() -> None:
    op.drop_constraint("uq_users_google_sub", "users", type_="unique")
    op.drop_column("users", "google_sub")
    op.alter_column("users", "password_hash", existing_type=sa.String(length=255), nullable=False)