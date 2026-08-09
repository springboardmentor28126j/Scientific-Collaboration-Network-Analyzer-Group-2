"""fix collaborationrequeststatus enum to use lowercase values

Revision ID: 0016_fix_collaboration_enum
Revises: 0015_projects
Create Date: 2026-08-04

"""
from alembic import op

revision = "0016_fix_collaboration_enum"
down_revision = "0015_projects"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE collaborationrequeststatus RENAME VALUE 'PENDING' TO 'pending'")
    op.execute("ALTER TYPE collaborationrequeststatus RENAME VALUE 'ACCEPTED' TO 'accepted'")
    op.execute("ALTER TYPE collaborationrequeststatus RENAME VALUE 'REJECTED' TO 'rejected'")
    op.execute("ALTER TYPE collaborationrequeststatus RENAME VALUE 'CANCELLED' TO 'cancelled'")


def downgrade() -> None:
    op.execute("ALTER TYPE collaborationrequeststatus RENAME VALUE 'pending' TO 'PENDING'")
    op.execute("ALTER TYPE collaborationrequeststatus RENAME VALUE 'accepted' TO 'ACCEPTED'")
    op.execute("ALTER TYPE collaborationrequeststatus RENAME VALUE 'rejected' TO 'REJECTED'")
    op.execute("ALTER TYPE collaborationrequeststatus RENAME VALUE 'cancelled' TO 'CANCELLED'")