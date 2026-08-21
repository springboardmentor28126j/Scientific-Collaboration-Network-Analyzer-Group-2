"""add departments

Revision ID: d8f1a2b3c4d5
Revises: c6e8a9d3f410
"""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision: str = "d8f1a2b3c4d5"
down_revision: str | Sequence[str] | None = "c6e8a9d3f410"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.create_table("departments", sa.Column("institution_id", sa.UUID(), nullable=False), sa.Column("name", sa.String(255), nullable=False), sa.Column("description", sa.Text()), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("institution_id", "name", name="uq_department_institution_name"))
    op.create_index("ix_departments_institution_id", "departments", ["institution_id"])

def downgrade() -> None:
    op.drop_index("ix_departments_institution_id", table_name="departments")
    op.drop_table("departments")
