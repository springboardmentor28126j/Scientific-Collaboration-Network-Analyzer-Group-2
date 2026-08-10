"""project, project_member tables

Revision ID: 0015_projects
Revises: 0014_collaborations
Create Date: 2026-08-05

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
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("planning", "active", "on_hold", "completed", name="projectstatus"),
            nullable=False,
            server_default="planning",
        ),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("funding_source", sa.String(length=255), nullable=True),
        sa.Column("budget", sa.Numeric(14, 2), nullable=True),
        sa.Column(
            "institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=True
        ),
        sa.Column(
            "lead_researcher_id",
            sa.Integer(),
            sa.ForeignKey("researchers.id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_projects_institution_id", "projects", ["institution_id"])
    op.create_index("ix_projects_lead_researcher_id", "projects", ["lead_researcher_id"])
    op.create_index("ix_projects_status", "projects", ["status"])

    op.create_table(
        "project_members",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False
        ),
        sa.Column(
            "researcher_id", sa.Integer(), sa.ForeignKey("researchers.id"), nullable=False
        ),
        sa.Column(
            "role_in_project",
            sa.Enum("lead", "co_investigator", "member", name="projectrole"),
            nullable=False,
            server_default="member",
        ),
        sa.Column("joined_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("project_id", "researcher_id", name="uq_project_researcher"),
    )
    op.create_index("ix_project_members_project_id", "project_members", ["project_id"])
    op.create_index(
        "ix_project_members_researcher_id", "project_members", ["researcher_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_project_members_researcher_id", table_name="project_members")
    op.drop_index("ix_project_members_project_id", table_name="project_members")
    op.drop_table("project_members")
    sa.Enum(name="projectrole").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_projects_status", table_name="projects")
    op.drop_index("ix_projects_lead_researcher_id", table_name="projects")
    op.drop_index("ix_projects_institution_id", table_name="projects")
    op.drop_table("projects")
    sa.Enum(name="projectstatus").drop(op.get_bind(), checkfirst=True)
