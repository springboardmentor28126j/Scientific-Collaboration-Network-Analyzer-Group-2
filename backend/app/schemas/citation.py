from datetime import datetime

from pydantic import BaseModel, model_validator


class CitationCreate(BaseModel):
    cited_publication_id: int | None = None
    external_title: str | None = None
    external_authors: str | None = None
    external_venue: str | None = None
    external_year: int | None = None
    external_doi: str | None = None
    context: str | None = None

    @model_validator(mode="after")
    def validate_single_target(self):
        has_internal = self.cited_publication_id is not None
        has_external = bool(self.external_title and self.external_title.strip())
        if not has_internal and not has_external:
            raise ValueError("Provide either cited_publication_id or external_title")
        if has_internal and has_external:
            raise ValueError("Provide either cited_publication_id or external fields, not both")
        return self


class CitationOut(BaseModel):
    citation_id: int
    citing_publication_id: int
    citing_publication_title: str

    cited_publication_id: int | None
    is_internal: bool

    display_title: str
    display_authors: str | None
    display_venue: str | None
    display_year: int | None
    display_doi: str | None

    context: str | None
    added_by_researcher_id: int
    added_by_name: str
    created_at: datetime


class CitationListResponse(BaseModel):
    items: list[CitationOut]
    total: int


class CitationTextOut(BaseModel):
    apa: str
    mla: str
    bibtex: str