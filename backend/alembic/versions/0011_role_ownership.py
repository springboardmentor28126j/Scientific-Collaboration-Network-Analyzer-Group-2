"""role-based ownership: institution admin_user_id, conference institution_id

Revision ID: 0011_role_ownership
Revises: 0010_publication_type
Create Date: 2026-07-27

"""
from alembic import op
import sqlalchemy as sa

revision = "0011_role_ownership"
down_revision = "0010_publication_type"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Nullable: existing institutions/conferences won't have an owner until
    # a System Admin assigns one (institutions) or new conferences are
    # created going forward (conferences, enforced as required at the API
    # layer even though the DB column stays nullable for old rows).
    op.add_column(
        "institutions",
        sa.Column("admin_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.add_column(
        "conferences",
        sa.Column(
            "institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=True
        ),
    )


def downgrade() -> None:
    op.drop_column("conferences", "institution_id")
    op.drop_column("institutions", "admin_user_id")
