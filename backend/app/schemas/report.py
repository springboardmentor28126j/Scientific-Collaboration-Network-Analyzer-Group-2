from pydantic import BaseModel


class SummaryReportOut(BaseModel):
    scope: str  # "system", "institution", or "researcher"
    researcher_count: int | None = None
    institution_count: int | None = None
    publication_count: int
    published_publication_count: int
    project_count: int
    active_project_count: int
    conference_count: int | None = None
    collaboration_count: int | None = None


class CountByKey(BaseModel):
    key: str
    count: int


class PublicationReportOut(BaseModel):
    scope: str
    total: int
    by_status: list[CountByKey]
    by_type: list[CountByKey]
    by_year: list[CountByKey]


class ProjectReportOut(BaseModel):
    scope: str
    total: int
    by_status: list[CountByKey]


class CollaborationReportOut(BaseModel):
    scope: str
    total_collaborations: int
    total_pending_requests: int
    average_strength: float
    top_collaborations: list["TopCollaborationOut"]


class TopCollaborationOut(BaseModel):
    collaboration_id: int
    researcher1_email: str
    researcher2_email: str
    strength: int


class InstitutionReportRow(BaseModel):
    institution_id: int
    name: str
    researcher_count: int
    publication_count: int
    project_count: int


class InstitutionReportOut(BaseModel):
    rows: list[InstitutionReportRow]
