"""reviewer assignments + publication review fields

Revision ID: 0012_reviewer_assignments
Revises: 0011_role_ownership
Create Date: 2026-07-27

"""
from alembic import op
import sqlalchemy as sa

revision = "0012_reviewer_assignments"
down_revision = "0011_role_ownership"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reviewer_assignments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "reviewer_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=True
        ),
        sa.Column(
            "publication_id", sa.Integer(), sa.ForeignKey("publications.id"), nullable=True
        ),
        sa.Column("assigned_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "(institution_id IS NOT NULL) != (publication_id IS NOT NULL)",
            name="ck_reviewer_assignment_exactly_one_scope",
        ),
    )

    # Nullable: existing publications won't have review info until a
    # reviewer actually reviews them.
    op.add_column(
        "publications",
        sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.add_column("publications", sa.Column("review_comment", sa.Text(), nullable=True))
    op.add_column("publications", sa.Column("reviewed_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("publications", "reviewed_at")
    op.drop_column("publications", "review_comment")
    op.drop_column("publications", "reviewed_by")
    op.drop_table("reviewer_assignments")