"""conference metadata: conference type, registration timestamp

Revision ID: 0004_conference_metadata
Revises: 0003_conference_enhancements
Create Date: 2026-07-21

"""
from alembic import op
import sqlalchemy as sa

revision = "0004_conference_metadata"
down_revision = "0003_conference_enhancements"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conference_type = sa.Enum(
        "in_person", "virtual", "hybrid", name="conferencetype"
    )
    conference_type.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "conferences",
        sa.Column("conference_type", conference_type, nullable=True),
    )

    op.add_column(
        "conference_attendances",
        sa.Column(
            "registered_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_column("conference_attendances", "registered_at")
    op.drop_column("conferences", "conference_type")
    sa.Enum(name="conferencetype").drop(op.get_bind(), checkfirst=True)