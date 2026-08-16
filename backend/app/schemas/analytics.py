from pydantic import BaseModel


class TopPaperOut(BaseModel):
    publication_id: int
    title: str
    citation_count: int


class InfluentialPaperOut(BaseModel):
    publication_id: int
    title: str
    influence_score: int


class TopResearcherOut(BaseModel):
    researcher_id: int
    name: str
    total_citations: int
    publication_count: int


class TopInstitutionOut(BaseModel):
    institution_id: int
    name: str
    total_citations: int
    publication_count: int
    avg_citations_per_publication: float


class CitationAnalyticsOut(BaseModel):
    top_papers: list[TopPaperOut]
    influential_papers: list[InfluentialPaperOut]
    top_researchers: list[TopResearcherOut]
    top_institutions: list[TopInstitutionOut]