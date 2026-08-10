"""collaboration_request, collaboration, collaboration_publication tables

Revision ID: 0014_collaborations
Revises: 0013_citations
Create Date: 2026-08-03

"""
from alembic import op
import sqlalchemy as sa

revision = "0014_collaborations"
down_revision = "0013_citations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collaboration_requests",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "requester_id", sa.Integer(), sa.ForeignKey("researchers.id"), nullable=False
        ),
        sa.Column(
            "addressee_id", sa.Integer(), sa.ForeignKey("researchers.id"), nullable=False
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "accepted",
                "rejected",
                "cancelled",
                name="collaborationrequeststatus",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "requester_id != addressee_id", name="ck_collaboration_request_not_self"
        ),
    )
    op.create_index(
        "ix_collaboration_requests_requester_id", "collaboration_requests", ["requester_id"]
    )
    op.create_index(
        "ix_collaboration_requests_addressee_id", "collaboration_requests", ["addressee_id"]
    )
    op.create_index(
        "ix_collaboration_requests_status", "collaboration_requests", ["status"]
    )

    op.create_table(
        "collaborations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "researcher1_id", sa.Integer(), sa.ForeignKey("researchers.id"), nullable=False
        ),
        sa.Column(
            "researcher2_id", sa.Integer(), sa.ForeignKey("researchers.id"), nullable=False
        ),
        sa.Column("strength", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("first_collaboration", sa.Date(), nullable=True),
        sa.Column("last_collaboration", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "researcher1_id", "researcher2_id", name="uq_collaboration_pair"
        ),
        sa.CheckConstraint(
            "researcher1_id < researcher2_id", name="ck_collaboration_ordered_pair"
        ),
    )
    op.create_index(
        "ix_collaborations_researcher1_id", "collaborations", ["researcher1_id"]
    )
    op.create_index(
        "ix_collaborations_researcher2_id", "collaborations", ["researcher2_id"]
    )

    op.create_table(
        "collaboration_publications",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "collaboration_id",
            sa.Integer(),
            sa.ForeignKey("collaborations.id"),
            nullable=False,
        ),
        sa.Column(
            "publication_id",
            sa.Integer(),
            sa.ForeignKey("publications.id"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "collaboration_id", "publication_id", name="uq_collaboration_publication"
        ),
    )
    op.create_index(
        "ix_collaboration_publications_collaboration_id",
        "collaboration_publications",
        ["collaboration_id"],
    )
    op.create_index(
        "ix_collaboration_publications_publication_id",
        "collaboration_publications",
        ["publication_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_collaboration_publications_publication_id",
        table_name="collaboration_publications",
    )
    op.drop_index(
        "ix_collaboration_publications_collaboration_id",
        table_name="collaboration_publications",
    )
    op.drop_table("collaboration_publications")

    op.drop_index("ix_collaborations_researcher2_id", table_name="collaborations")
    op.drop_index("ix_collaborations_researcher1_id", table_name="collaborations")
    op.drop_table("collaborations")

    op.drop_index("ix_collaboration_requests_status", table_name="collaboration_requests")
    op.drop_index(
        "ix_collaboration_requests_addressee_id", table_name="collaboration_requests"
    )
    op.drop_index(
        "ix_collaboration_requests_requester_id", table_name="collaboration_requests"
    )
    op.drop_table("collaboration_requests")

    sa.Enum(name="collaborationrequeststatus").drop(op.get_bind(), checkfirst=True)
