"""initial schema: users, institutions, researchers

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-02

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    user_role = sa.Enum(
        "researcher", "institution_admin", "reviewer", "system_admin", name="userrole"
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="researcher"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "institutions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "researchers",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "institution_id",
            sa.Integer(),
            sa.ForeignKey("institutions.id"),
            nullable=True,
        ),
        sa.Column("department", sa.String(255), nullable=True),
        sa.Column("research_interests", sa.Text(), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("affiliations", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("researchers")
    op.drop_table("institutions")
    op.drop_table("users")
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)
