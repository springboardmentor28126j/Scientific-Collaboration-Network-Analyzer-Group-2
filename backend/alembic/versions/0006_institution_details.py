"""institutions: expand to full institution management fields

Revision ID: 0006_institution_details
Revises: 0005_conference_sessions
Create Date: 2026-07-22

"""
from alembic import op
import sqlalchemy as sa

revision = "0006_institution_details"
down_revision = "0005_conference_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns as nullable first so this works even if the
    # institutions table already has rows (existing rows get NULL
    # until backfilled).
    op.add_column("institutions", sa.Column("short_name", sa.String(50), nullable=True))
    op.add_column("institutions", sa.Column("institution_type", sa.String(100), nullable=True))
    op.add_column("institutions", sa.Column("email", sa.String(255), nullable=True))
    op.add_column("institutions", sa.Column("phone", sa.String(20), nullable=True))
    op.add_column("institutions", sa.Column("website", sa.String(255), nullable=True))
    op.add_column("institutions", sa.Column("city", sa.String(100), nullable=True))
    op.add_column("institutions", sa.Column("state", sa.String(100), nullable=True))
    op.add_column("institutions", sa.Column("country", sa.String(100), nullable=True))
    op.add_column("institutions", sa.Column("postal_code", sa.String(20), nullable=True))
    op.add_column(
        "institutions",
        sa.Column("status", sa.String(20), nullable=False, server_default="Active"),
    )

    # Backfill any pre-existing rows with placeholder values so the
    # NOT NULL + UNIQUE constraints below don't fail on real data.
    op.execute(
        "UPDATE institutions SET email = 'unknown-' || id || '@placeholder.local' "
        "WHERE email IS NULL"
    )
    op.execute("UPDATE institutions SET city = 'Unknown' WHERE city IS NULL")
    op.execute("UPDATE institutions SET state = 'Unknown' WHERE state IS NULL")
    op.execute("UPDATE institutions SET country = 'Unknown' WHERE country IS NULL")

    # Now enforce the real constraints.
    op.alter_column("institutions", "email", existing_type=sa.String(255), nullable=False)
    op.alter_column("institutions", "city", existing_type=sa.String(100), nullable=False)
    op.alter_column("institutions", "state", existing_type=sa.String(100), nullable=False)
    op.alter_column("institutions", "country", existing_type=sa.String(100), nullable=False)
    op.create_unique_constraint("uq_institutions_email", "institutions", ["email"])


def downgrade() -> None:
    op.drop_constraint("uq_institutions_email", "institutions", type_="unique")
    op.drop_column("institutions", "status")
    op.drop_column("institutions", "postal_code")
    op.drop_column("institutions", "country")
    op.drop_column("institutions", "state")
    op.drop_column("institutions", "city")
    op.drop_column("institutions", "website")
    op.drop_column("institutions", "phone")
    op.drop_column("institutions", "email")
    op.drop_column("institutions", "institution_type")
    op.drop_column("institutions", "short_name")
