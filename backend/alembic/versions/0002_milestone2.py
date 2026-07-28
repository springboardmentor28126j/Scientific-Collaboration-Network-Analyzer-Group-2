"""milestone 2: publications, conferences

Revision ID: 0002_milestone2
Revises: 0001_initial
Create Date: 2026-07-14

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_milestone2"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    attendance_role = sa.Enum("presenter", "attendee", name="attendancerole")

    op.create_table(
        "publications",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("venue", sa.String(255), nullable=True),
        sa.Column("doi_link", sa.String(500), nullable=True),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "publication_authors",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "publication_id",
            sa.Integer(),
            sa.ForeignKey("publications.id"),
            nullable=False,
        ),
        sa.Column(
            "researcher_id",
            sa.Integer(),
            sa.ForeignKey("researchers.id"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "publication_id", "researcher_id", name="uq_publication_researcher"
        ),
    )

    op.create_table(
        "conferences",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("website_link", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "conference_attendances",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "conference_id",
            sa.Integer(),
            sa.ForeignKey("conferences.id"),
            nullable=False,
        ),
        sa.Column(
            "researcher_id",
            sa.Integer(),
            sa.ForeignKey("researchers.id"),
            nullable=False,
        ),
        sa.Column("role", attendance_role, nullable=False, server_default="attendee"),
        sa.UniqueConstraint(
            "conference_id", "researcher_id", name="uq_conference_researcher"
        ),
    )


def downgrade() -> None:
    op.drop_table("conference_attendances")
    op.drop_table("conferences")
    op.drop_table("publication_authors")
    op.drop_table("publications")
    sa.Enum(name="attendancerole").drop(op.get_bind(), checkfirst=True)