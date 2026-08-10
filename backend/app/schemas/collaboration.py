from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.collaboration import CollaborationRequestStatus


class ResearcherBrief(BaseModel):
    """Small, embeddable researcher summary -- avoids forcing the frontend
    to make a second round trip just to show who's on the other end of a
    connection, request, or graph node. Workspace researchers have no
    first/last name field, so email (via the linked user) stands in as the
    display identity, same as citations.html / citation_insights.html
    already do for authors."""

    model_config = ConfigDict(from_attributes=True)

    researcher_id: int
    email: str
    department: str | None = None
    institution_id: int | None = None


# --- Collaboration requests (the "connect" / "accept" flow) ---

class CollaborationRequestCreate(BaseModel):
    addressee_researcher_id: int
    message: str | None = Field(default=None, max_length=1000)


class CollaborationRequestRespond(BaseModel):
    """Only a subset of CollaborationRequestStatus is a valid client-supplied
    transition -- PENDING is a default state, never something to PATCH into."""

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


# --- Established collaborations (the network edges) ---

class SharedPublicationOut(BaseModel):
    publication_id: int
    title: str
    year: int | None = None


class CollaborationOut(BaseModel):
    id: int
    researcher1: ResearcherBrief
    researcher2: ResearcherBrief
    # Whichever of researcher1/researcher2 isn't "me" -- lets the frontend
    # render "My Collaborators" without comparing IDs itself. Only populated
    # by endpoints called in the context of a specific viewer; None for
    # viewer-agnostic responses.
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


# --- Network graph ---

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


# --- Suggested collaborators ---

class SuggestedCollaboratorOut(BaseModel):
    researcher: ResearcherBrief
    reason: str
    mutual_collaborator_count: int = 0
