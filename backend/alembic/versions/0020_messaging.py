"""in-app messaging: conversations scoped to a project or a collaboration,
messages, and per-researcher read tracking

Revision ID: 0020_messaging
Revises: 0019_google_signin
Create Date: 2026-08-06

"""
from alembic import op
import sqlalchemy as sa

revision = "0020_messaging"
down_revision = "0019_google_signin"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=True),
        sa.Column(
            "collaboration_id",
            sa.Integer(),
            sa.ForeignKey("collaborations.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("project_id", name="uq_conversation_project"),
        sa.UniqueConstraint("collaboration_id", name="uq_conversation_collaboration"),
        sa.CheckConstraint(
            "(project_id IS NOT NULL AND collaboration_id IS NULL) OR "
            "(project_id IS NULL AND collaboration_id IS NOT NULL)",
            name="ck_conversation_exactly_one_scope",
        ),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "conversation_id", sa.Integer(), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "sender_researcher_id",
            sa.Integer(),
            sa.ForeignKey("researchers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "conversation_reads",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "conversation_id", sa.Integer(), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "researcher_id", sa.Integer(), sa.ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("last_read_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("conversation_id", "researcher_id", name="uq_conversation_read"),
    )


def downgrade() -> None:
    op.drop_table("conversation_reads")
    op.drop_table("messages")
    op.drop_table("conversations")
    