from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class Citation(Base):
    """One row = 'citing_publication cites cited_publication (or an
    external paper)'.

    The cited paper is either:
      - internal: cited_publication_id points at a Publication already
        in SCNA (counts toward that paper's/its authors'/their
        institution's citation stats and appears in the network graph), or
      - external: cited_publication_id is NULL and cited_title (+
        optional authors/year/venue) is filled in as free text, for
        papers outside the system.

    Exactly one of those two must be set, enforced by a CheckConstraint
    at the DB level and mirrored in the Pydantic schema.
    """

    __tablename__ = "citations"
    __table_args__ = (
        CheckConstraint(
            "(cited_publication_id IS NOT NULL) OR (cited_title IS NOT NULL)",
            name="ck_citation_has_target",
        ),
        CheckConstraint(
            "citing_publication_id != cited_publication_id",
            name="ck_citation_no_self_cite",
        ),
        UniqueConstraint(
            "citing_publication_id", "cited_publication_id", name="uq_citation_pair"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    citing_publication_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("publications.id"), nullable=False, index=True
    )
    cited_publication_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("publications.id"), nullable=True, index=True
    )

    cited_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cited_authors: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cited_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cited_venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_by_researcher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    citing_publication: Mapped["Publication"] = relationship(
        "Publication", foreign_keys=[citing_publication_id]
    )
    cited_publication: Mapped[Optional["Publication"]] = relationship(
        "Publication", foreign_keys=[cited_publication_id]
    )
    created_by: Mapped["Researcher"] = relationship(
        "Researcher", foreign_keys=[created_by_researcher_id]
    )
