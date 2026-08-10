"""conference module enhancements: roles, status, presentation files, ownership

Revision ID: 0003_conference_enhancements
Revises: 0002_milestone2
Create Date: 2026-07-20

"""
from alembic import op
import sqlalchemy as sa

revision = "0003_conference_enhancements"
down_revision = "0002_milestone2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Postgres requires new enum values to be committed before they can be used,
    # so this runs outside the wrapping transaction.
    op.execute("COMMIT")
    op.execute("ALTER TYPE attendancerole ADD VALUE IF NOT EXISTS 'organizer'")
    op.execute("ALTER TYPE attendancerole ADD VALUE IF NOT EXISTS 'reviewer'")

    participation_status = sa.Enum(
        "registered", "confirmed", "cancelled", "attended", name="participationstatus"
    )
    participation_status.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "conference_attendances",
        sa.Column("status", participation_status, nullable=False, server_default="registered"),
    )
    op.add_column(
        "conference_attendances", sa.Column("presentation_title", sa.String(500), nullable=True)
    )
    op.add_column(
        "conference_attendances", sa.Column("stored_filename", sa.String(255), nullable=True)
    )
    op.add_column(
        "conference_attendances", sa.Column("original_filename", sa.String(255), nullable=True)
    )

    # Nullable so existing conferences created before this column existed remain valid.
    op.add_column(
        "conferences",
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("conferences", "created_by")
    op.drop_column("conference_attendances", "original_filename")
    op.drop_column("conference_attendances", "stored_filename")
    op.drop_column("conference_attendances", "presentation_title")
    op.drop_column("conference_attendances", "status")
    sa.Enum(name="participationstatus").drop(op.get_bind(), checkfirst=True)
    # Note: Postgres doesn't support removing individual enum values;
    # 'organizer'/'reviewer' remain on attendancerole after downgrade.
