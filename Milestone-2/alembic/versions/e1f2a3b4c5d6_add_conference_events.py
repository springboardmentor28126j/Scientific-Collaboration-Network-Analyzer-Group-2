"""add conference events

Revision ID: e1f2a3b4c5d6
Revises: d8f1a2b3c4d5
"""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision: str = "e1f2a3b4c5d6"
down_revision: str | Sequence[str] | None = "d8f1a2b3c4d5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.create_table("conference_events", sa.Column("conference_id", sa.UUID(), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False), sa.Column("ends_at", sa.DateTime(timezone=True)), sa.Column("description", sa.Text()), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.ForeignKeyConstraint(["conference_id"], ["conferences.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_conference_events_conference_id", "conference_events", ["conference_id"])

def downgrade() -> None:
    op.drop_index("ix_conference_events_conference_id", table_name="conference_events")
    op.drop_table("conference_events")
