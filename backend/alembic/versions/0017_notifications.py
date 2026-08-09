"""notifications table

Revision ID: 0017_notifications
Revises: 0016_fix_collaboration_enum
Create Date: 2026-08-05

"""
from alembic import op
import sqlalchemy as sa

revision = "0017_notifications"
down_revision = "0016_fix_collaboration_enum"
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
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_notifications_recipient_user_id", "notifications", ["recipient_user_id"])
    op.create_index("ix_notifications_recipient_is_read", "notifications", ["recipient_user_id", "is_read"])


def downgrade() -> None:
    op.drop_index("ix_notifications_recipient_is_read", table_name="notifications")
    op.drop_index("ix_notifications_recipient_user_id", table_name="notifications")
    op.drop_table("notifications")