from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class PublicationBrief(BaseModel):
    """Minimal publication info for nesting inside citation responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    year: int | None = None


class CitationBase(BaseModel):
    citing_publication_id: int
    cited_publication_id: int | None = None
    cited_title: str | None = None
    cited_authors: str | None = None
    cited_year: int | None = None
    cited_venue: str | None = None


class CitationCreate(CitationBase):
    @model_validator(mode="after")
    def _check_target_and_self_cite(self) -> "CitationCreate":
        if self.cited_publication_id is None and not self.cited_title:
            raise ValueError(
                "Provide either cited_publication_id (an existing publication) "
                "or at least cited_title (for an external citation)."
            )
        if (
            self.cited_publication_id is not None
            and self.cited_publication_id == self.citing_publication_id
        ):
            raise ValueError("A publication cannot cite itself.")
        return self


class CitationOut(CitationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_researcher_id: int
    created_at: datetime
    citing_publication: PublicationBrief
    cited_publication: PublicationBrief | None = None


class TopPaperOut(BaseModel):
    publication_id: int
    title: str
    year: int | None = None
    citation_count: int


class TopAuthorOut(BaseModel):
    researcher_id: int
    email: str
    citation_count: int


class TopInstitutionOut(BaseModel):
    institution_id: int
    name: str
    citation_count: int


class CitationNetworkNode(BaseModel):
    id: int
    label: str
    year: int | None = None
    researcher_ids: list[int] = []
    institution_id: int | None = None


class CitationNetworkEdge(BaseModel):
    source: int
    target: int


class CitationNetworkOut(BaseModel):
    nodes: list[CitationNetworkNode]
    edges: list[CitationNetworkEdge]