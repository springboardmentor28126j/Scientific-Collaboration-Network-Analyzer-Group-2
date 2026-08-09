"""auth tokens, audit logs, user email verification flag

Revision ID: 0018_auth_audit
Revises: 0017_notifications
Create Date: 2026-08-05

"""
from alembic import op
import sqlalchemy as sa

revision = "0018_auth_audit"
down_revision = "0017_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # server_default=true() grandfathers in every existing account (including
    # the ones you're using to test right now) so nobody gets locked out.
    # New self-registrations explicitly set is_verified=False in code (Part C).
    op.add_column(
        "users", sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.true())
    )

    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(64), nullable=False, unique=True),
        sa.Column(
            "token_type",
            sa.Enum("email_verification", "password_reset", name="authtokentype"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_auth_tokens_token", "auth_tokens", ["token"], unique=True)
    op.create_index("ix_auth_tokens_user_id", "auth_tokens", ["user_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_auth_tokens_user_id", table_name="auth_tokens")
    op.drop_index("ix_auth_tokens_token", table_name="auth_tokens")
    op.drop_table("auth_tokens")
    sa.Enum(name="authtokentype").drop(op.get_bind(), checkfirst=True)

    op.drop_column("users", "is_verified")