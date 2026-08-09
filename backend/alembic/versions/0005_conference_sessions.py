"""conference sessions: event scheduling / agenda

Revision ID: 0005_conference_sessions
Revises: 0004_conference_metadata
Create Date: 2026-07-21

"""
from alembic import op
import sqlalchemy as sa

revision = "0005_conference_sessions"
down_revision = "0004_conference_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conference_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "conference_id", sa.Integer(), sa.ForeignKey("conferences.id"), nullable=False
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("room", sa.String(255), nullable=True),
        sa.Column(
            "speaker_participation_id",
            sa.Integer(),
            sa.ForeignKey("conference_attendances.id"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("conference_sessions")