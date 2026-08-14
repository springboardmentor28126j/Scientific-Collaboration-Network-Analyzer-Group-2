"""add mfa_enabled and mfa_otp token type

Revision ID: 0021_mfa_otp
Revises: 0021_project_member_backfill
Create Date: 2026-08-14

Context: same "shared DB, diverged local chains" story as 0017_reconcile_drift
/ 0019_capstone_stamp / 0020_auth_tokens. A teammate ran their reference
project's own migration chain (which has a node literally named
"0021_mfa_otp", chained after their own "0020_messaging") against this
same live DB, advancing alembic_version to "0021_mfa_otp" -- a revision
ID that doesn't exist anywhere in *this* repo's alembic/versions/, so
`alembic upgrade head` failed with "Can't locate revision identified by
'0021_mfa_otp'".

This file's revision ID is deliberately set to that EXACT string (not
"0022_mfa_otp", despite the filename) so this repo's script directory
recognizes the DB's current stamp again. down_revision points at this
repo's own actual current head ("0021_project_member_backfill"), not at
the reference chain's "0020_messaging" (which doesn't exist here).

The upgrade() below re-implements the *same* schema change the
reference migration made (users.mfa_enabled + the 'mfa_otp' enum value),
written idempotently per the 0020_auth_tokens precedent: since
alembic_version is already stamped past this point on the live DB, a
plain `alembic upgrade head` will treat current==head and skip calling
upgrade() entirely -- but the idempotent checks here mean this migration
is also safe to run for real (e.g. against a fresh/clean DB, or after an
`alembic stamp` reset) without erroring on a duplicate column/enum value.
"""
from alembic import op
import sqlalchemy as sa

revision = "0021_mfa_otp"
down_revision = "0021_project_member_backfill"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_columns = {c["name"] for c in inspector.get_columns("users")}
    if "mfa_enabled" not in existing_columns:
        op.add_column(
            "users",
            sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        )

    # Postgres enum values can only be added outside/alongside existing
    # values, never removed -- IF NOT EXISTS makes this safe to re-run.
    op.execute("ALTER TYPE authtokentype ADD VALUE IF NOT EXISTS 'mfa_otp'")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {c["name"] for c in inspector.get_columns("users")}
    if "mfa_enabled" in existing_columns:
        op.drop_column("users", "mfa_enabled")
    # Postgres doesn't support removing individual enum values -- no-op.
