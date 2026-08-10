"""capstone no-op -- resolve alembic_version drift

Revision ID: 0019_capstone_stamp
Revises: 0018_notifications
Create Date: 2026-08-06

Context: the shared local Postgres instance is used by both this project
and a teammate's reference copy (Group-2). Running the reference
project's own migration chain against that same DB silently advanced its
alembic_version row to "0019_google_signin" -- a revision ID that only
exists in the *reference* project's versions/ folder, not this one. That
left `alembic upgrade head` in this project unable to locate the current
stamp ("Can't locate revision identified by '0019_google_signin'"),
even though the actual table shapes were reconciled and adopted as
ground truth in models/ (see 0017_reconcile_drift, 0018_notifications).

This migration does no DDL -- both tables (notifications, plus everything
reconciled in 0017) already exist in the live DB in their final shape.
It exists purely so this chain has a head revision ID
("0019_capstone_stamp") to stamp the DB to via:

    cd backend
    alembic stamp --purge 0019_capstone_stamp

`--purge` clears the alembic_version table first (removing the foreign
"0019_google_signin" row) before writing this migration's ID as the new
single stamp. After that, `alembic upgrade head` reports "no upgrades
needed, already at head" instead of erroring, with zero DDL ever
executed against the live DB by this file.
"""
from alembic import op
import sqlalchemy as sa

revision = "0019_capstone_stamp"
down_revision = "0018_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op by design -- see module docstring."""
    pass


def downgrade() -> None:
    """No-op by design -- see module docstring."""
    pass
