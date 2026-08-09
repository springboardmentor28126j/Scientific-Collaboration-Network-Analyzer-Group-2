"""project, project_member tables

Revision ID: 0015_projects
Revises: 0014_collaborations
Create Date: 2026-08-04

"""
from alembic import op
import sqlalchemy as sa

revision = "0015_projects"
down_revision = "0014_collaborations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("planned", "ongoing", "completed", "cancelled", name="projectstatus"),
            nullable=False,
            server_default="planned",
        ),
        sa.Column("lead_researcher_id", sa.Integer(), sa.ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_projects_lead_researcher_id", "projects", ["lead_researcher_id"])

    op.create_table(
        "project_members",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("researcher_id", sa.Integer(), sa.ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "role",
            sa.Enum("lead", "member", name="projectmemberrole"),
            nullable=False,
            server_default="member",
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "accepted", "declined", name="projectmemberstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("invited_by_id", sa.Integer(), sa.ForeignKey("researchers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.Column("joined_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("project_id", "researcher_id", name="uq_project_member"),
    )
    op.create_index("ix_project_members_project_id", "project_members", ["project_id"])
    op.create_index("ix_project_members_researcher_id", "project_members", ["researcher_id"])


def downgrade() -> None:
    op.drop_index("ix_project_members_researcher_id", table_name="project_members")
    op.drop_index("ix_project_members_project_id", table_name="project_members")
    op.drop_table("project_members")
    sa.Enum(name="projectmemberstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="projectmemberrole").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_projects_lead_researcher_id", table_name="projects")
    op.drop_table("projects")
    sa.Enum(name="projectstatus").drop(op.get_bind(), checkfirst=True)