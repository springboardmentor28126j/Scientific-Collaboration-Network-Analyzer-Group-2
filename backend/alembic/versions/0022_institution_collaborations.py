"""add institution_collaborations table

Revision ID: 0022_institution_collaborations
Revises: 0021_mfa_otp
Create Date: 2026-08-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0022_institution_collaborations"
down_revision = "0021_mfa_otp"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use the Postgres-native ENUM type directly. Using the generic
    # sa.Enum(..., create_type=False) here does NOT work reliably —
    # SQLAlchemy converts it to postgresql.ENUM internally and drops
    # the create_type=False flag in that conversion, causing
    # create_table() below to try to CREATE TYPE a second time.
    institution_collab_status = postgresql.ENUM(
        "pending", "active", "ended",
        name="institutioncollaborationstatus",
        create_type=False,
    )

    # Create the type once, safely, checking first.
    institution_collab_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "institution_collaborations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("institution1_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("institution2_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", institution_collab_status, nullable=False, server_default="pending"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("institution1_id != institution2_id", name="ck_institution_collab_not_self"),
        sa.UniqueConstraint("institution1_id", "institution2_id", name="uq_institution_collab_pair"),
    )


def downgrade() -> None:
    op.drop_table("institution_collaborations")
    postgresql.ENUM(name="institutioncollaborationstatus").drop(op.get_bind(), checkfirst=True)