from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, func, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Citation(Base):
    """
    A directed reference: citing_publication references either another
    publication already in this system (cited_publication_id) or a work
    outside it (the external_* fields). Exactly one of the two is set --
    enforced by ck_citation_has_target, the same "pick one target" pattern
    CollaborationRequest uses for ck_collaboration_request_not_self.
    """
    __tablename__ = "citation"

    citation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    citing_publication_id: Mapped[int] = mapped_column(
        ForeignKey("publication.publication_id", ondelete="CASCADE"), nullable=False
    )
    cited_publication_id: Mapped[int | None] = mapped_column(
        ForeignKey("publication.publication_id", ondelete="SET NULL"), nullable=True
    )

    external_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    external_authors: Mapped[str | None] = mapped_column(String(500), nullable=True)
    external_venue: Mapped[str | None] = mapped_column(String(300), nullable=True)
    external_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    external_doi: Mapped[str | None] = mapped_column(String(150), nullable=True)

    context: Mapped[str | None] = mapped_column(Text, nullable=True)

    added_by_id: Mapped[int] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "cited_publication_id IS NOT NULL OR external_title IS NOT NULL",
            name="ck_citation_has_target",
        ),
        CheckConstraint("citing_publication_id != cited_publication_id", name="ck_citation_not_self"),
        UniqueConstraint("citing_publication_id", "cited_publication_id", name="uq_citation_internal_pair"),
    )

    citing_publication: Mapped["Publication"] = relationship(foreign_keys=[citing_publication_id])
    cited_publication: Mapped["Publication | None"] = relationship(foreign_keys=[cited_publication_id])
    added_by: Mapped["ResearcherProfile"] = relationship()

    @property
    def is_internal(self) -> bool:
        return self.cited_publication_id is not None