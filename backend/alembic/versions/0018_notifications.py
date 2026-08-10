"""notifications table

Revision ID: 0018_notifications
Revises: 0017_reconcile_drift
Create Date: 2026-08-06

NOTE: this migration was never actually executed against this project's
shared dev DB. A notifications table already existed there (created by an
external migration chain sharing the same local Postgres instance -- see
check_notifications.py diagnostic, run 2026-08-06) with a real column
shape of recipient_user_id/type/message/link/is_read/created_at, no
title/entity_type/entity_id. That shape was adopted as ground truth
(app/models/notification.py aliases to it) instead of altering the table,
and this file's body was rewritten to match it so a genuinely fresh
install still produces a working, identical table from this chain alone.
The shared dev DB's bookkeeping was moved past this point directly via
'alembic stamp --purge 0018_notifications', not by running this upgrade().
"""
from alembic import op
import sqlalchemy as sa

revision = "0018_notifications"
down_revision = "0017_reconcile_drift"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("recipient_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("link", sa.String(length=255), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_notifications_recipient_user_id", "notifications", ["recipient_user_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])


def downgrade() -> None:
    op.drop_index("ix_notifications_is_read", table_name="notifications")
    op.drop_index("ix_notifications_recipient_user_id", table_name="notifications")
    op.drop_table("notifications")
