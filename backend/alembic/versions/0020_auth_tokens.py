"""auth tokens (password reset)

Revision ID: 0020_auth_tokens
Revises: 0019_capstone_stamp
Create Date: 2026-08-11

Adds the auth_tokens table backing the Forgot Password / Reset Password
flow (ported from the Group-2 reference project). Only password_reset is
actually issued today; email_verification is included in the enum for
future reuse but nothing in this project generates that type yet, so no
users.is_verified column is added here -- that belongs to a separate,
not-yet-requested email-verification feature.

This local Postgres DB is shared with the reference project (see
0017_reconcile_drift for the same story on projects/audit_logs), so the
authtokentype enum and/or the auth_tokens table itself may already exist
from a run of that other, longer migration chain even though this repo's
alembic_version hasn't recorded 0020 yet. Every step below is written
idempotently (checkfirst / existence checks) rather than assuming a
clean slate -- consistent with the "code-side compatibility only, no
further ALTER TABLE migrations" approach used for the rest of this drift.
The table shape here is identical to what that other chain creates (same
source), so reusing an existing table/type as-is is safe.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0020_auth_tokens"
down_revision = "0019_capstone_stamp"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    token_type_enum = postgresql.ENUM(
        "email_verification", "password_reset", name="authtokentype"
    )
    token_type_enum.create(bind, checkfirst=True)

    if "auth_tokens" not in inspector.get_table_names():
        op.create_table(
            "auth_tokens",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("token", sa.String(64), nullable=False, unique=True),
            sa.Column(
                "token_type",
                postgresql.ENUM(
                    "email_verification", "password_reset", name="authtokentype", create_type=False
                ),
                nullable=False,
            ),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("used_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )

    existing_indexes = {ix["name"] for ix in inspector.get_indexes("auth_tokens")} if "auth_tokens" in inspector.get_table_names() else set()
    if "ix_auth_tokens_token" not in existing_indexes:
        op.create_index("ix_auth_tokens_token", "auth_tokens", ["token"], unique=True)
    if "ix_auth_tokens_user_id" not in existing_indexes:
        op.create_index("ix_auth_tokens_user_id", "auth_tokens", ["user_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "auth_tokens" in inspector.get_table_names():
        existing_indexes = {ix["name"] for ix in inspector.get_indexes("auth_tokens")}
        if "ix_auth_tokens_user_id" in existing_indexes:
            op.drop_index("ix_auth_tokens_user_id", table_name="auth_tokens")
        if "ix_auth_tokens_token" in existing_indexes:
            op.drop_index("ix_auth_tokens_token", table_name="auth_tokens")
        op.drop_table("auth_tokens")
    postgresql.ENUM(name="authtokentype").drop(bind, checkfirst=True)
