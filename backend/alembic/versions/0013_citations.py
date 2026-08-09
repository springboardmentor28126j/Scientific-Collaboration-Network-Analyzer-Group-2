"""citations table

Revision ID: 0013_citations
Revises: 0012_reviewer_assignments
Create Date: 2026-07-30

"""
from alembic import op
import sqlalchemy as sa

revision = "0013_citations"
down_revision = "0012_reviewer_assignments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "citations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("citing_publication_id", sa.Integer(), sa.ForeignKey("publications.id"), nullable=False),
        sa.Column("cited_publication_id", sa.Integer(), sa.ForeignKey("publications.id"), nullable=True),
        sa.Column("cited_title", sa.String(length=500), nullable=True),
        sa.Column("cited_authors", sa.String(length=500), nullable=True),
        sa.Column("cited_year", sa.Integer(), nullable=True),
        sa.Column("cited_venue", sa.String(length=255), nullable=True),
        sa.Column("created_by_researcher_id", sa.Integer(), sa.ForeignKey("researchers.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "(cited_publication_id IS NOT NULL) OR (cited_title IS NOT NULL)",
            name="ck_citation_has_target",
        ),
        sa.CheckConstraint(
            "citing_publication_id != cited_publication_id",
            name="ck_citation_no_self_cite",
        ),
        sa.UniqueConstraint("citing_publication_id", "cited_publication_id", name="uq_citation_pair"),
    )
    op.create_index("ix_citations_citing_publication_id", "citations", ["citing_publication_id"])
    op.create_index("ix_citations_cited_publication_id", "citations", ["cited_publication_id"])


def downgrade() -> None:
    op.drop_index("ix_citations_cited_publication_id", table_name="citations")
    op.drop_index("ix_citations_citing_publication_id", table_name="citations")
    op.drop_table("citations")