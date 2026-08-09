from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.collaboration import CollaborationRequestStatus


class ResearcherBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    researcher_id: int
    email: str
    department: str | None = None
    institution_id: int | None = None


class CollaborationRequestCreate(BaseModel):
    addressee_researcher_id: int
    message: str | None = Field(default=None, max_length=1000)


class CollaborationRequestRespond(BaseModel):
    status: CollaborationRequestStatus

    def validate_is_response(self) -> None:
        if self.status not in (
            CollaborationRequestStatus.ACCEPTED,
            CollaborationRequestStatus.REJECTED,
            CollaborationRequestStatus.CANCELLED,
        ):
            raise ValueError("status must be one of: accepted, rejected, cancelled")


class CollaborationRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    requester: ResearcherBrief
    addressee: ResearcherBrief
    status: CollaborationRequestStatus
    message: str | None
    created_at: datetime
    responded_at: datetime | None


class CollaborationRequestListResponse(BaseModel):
    items: list[CollaborationRequestOut]
    total: int


class SharedPublicationOut(BaseModel):
    publication_id: int
    title: str
    year: int | None = None


class CollaborationOut(BaseModel):
    id: int
    researcher1: ResearcherBrief
    researcher2: ResearcherBrief
    partner: ResearcherBrief | None = None
    strength: int
    first_collaboration: date | None
    last_collaboration: date | None
    created_at: datetime


class CollaborationListResponse(BaseModel):
    items: list[CollaborationOut]
    total: int
    page: int
    page_size: int


class CollaborationDetailOut(CollaborationOut):
    shared_publications: list[SharedPublicationOut] = Field(default_factory=list)


class NetworkNode(BaseModel):
    researcher_id: int
    label: str
    department: str | None = None
    institution_id: int | None = None
    is_center: bool = False


class NetworkEdge(BaseModel):
    collaboration_id: int
    researcher1_id: int
    researcher2_id: int
    strength: int


class NetworkGraphOut(BaseModel):
    nodes: list[NetworkNode]
    edges: list[NetworkEdge]


class SuggestedCollaboratorOut(BaseModel):
    researcher: ResearcherBrief
    reason: str
    mutual_collaborator_count: int = 0