"""add institution_collaborations table

Revision ID: 0022_institution_collaborations
Revises: 0021_mfa_otp
Create Date: 2026-08-14

Context: same shared-DB drift pattern as 0021_mfa_otp / 0020_auth_tokens /
0017_reconcile_drift. A teammate's reference chain added this table
(chained off "0021_mfa_otp", which is already this repo's local head
after we fixed the previous drift) directly against the same live DB,
advancing alembic_version to "0022_institution_collaborations" -- a
revision this repo's local alembic/versions/ didn't have, causing
`alembic upgrade head` to fail with "Can't locate revision identified by
'0022_institution_collaborations'".

Filename is 0023 (this repo's own next number) but the revision id
below is deliberately the exact string already stamped on the shared DB,
same convention as 0022_mfa_otp.py's revision="0021_mfa_otp".

upgrade() replicates the teammate's table creation exactly, but with an
added checkfirst on the table itself (not just the enum type) so this
migration is also safe to actually run for real against a fresh DB.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0022_institution_collaborations"
down_revision = "0021_mfa_otp"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("institution_collaborations"):
        return

    # Use the Postgres-native ENUM type directly with create_type=False --
    # generic sa.Enum(..., create_type=False) doesn't reliably survive
    # SQLAlchemy's internal conversion to postgresql.ENUM, which can cause
    # create_table() below to try to CREATE TYPE a second time.
    institution_collab_status = postgresql.ENUM(
        "pending", "active", "ended",
        name="institutioncollaborationstatus",
        create_type=False,
    )
    institution_collab_status.create(bind, checkfirst=True)

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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("institution_collaborations"):
        op.drop_table("institution_collaborations")
    postgresql.ENUM(name="institutioncollaborationstatus").drop(bind, checkfirst=True)
