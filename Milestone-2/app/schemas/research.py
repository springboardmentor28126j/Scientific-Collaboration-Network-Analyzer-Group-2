import uuid
from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class ResearcherProfileUpdate(BaseModel):
    department: str | None = Field(default=None, max_length=255)
    skills: list[str] = Field(default_factory=list)
    research_interests: list[str] = Field(default_factory=list)
    affiliations: list[str] = Field(default_factory=list)


class ResearcherProfileRead(ResearcherProfileUpdate, ORMBase):
    id: uuid.UUID
    user_id: uuid.UUID


class PublicationStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class PublicationType(StrEnum):
    JOURNAL = "JOURNAL"
    CONFERENCE = "CONFERENCE"
    BOOK = "BOOK"
    PATENT = "PATENT"
    TECHNICAL_REPORT = "TECHNICAL_REPORT"


class PublicationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    abstract: str | None = None
    publication_type: PublicationType = PublicationType.JOURNAL
    status: PublicationStatus = PublicationStatus.DRAFT
    doi: str | None = Field(default=None, max_length=255)
    published_on: date | None = None
    file_url: str | None = Field(default=None, max_length=1000)
    author_ids: list[uuid.UUID] = Field(default_factory=list)


class PublicationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    abstract: str | None = None
    publication_type: PublicationType | None = None
    status: PublicationStatus | None = None
    doi: str | None = Field(default=None, max_length=255)
    published_on: date | None = None
    file_url: str | None = Field(default=None, max_length=1000)
    author_ids: list[uuid.UUID] | None = None


class PublicationRead(ORMBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    title: str
    abstract: str | None
    publication_type: PublicationType
    status: PublicationStatus
    doi: str | None
    published_on: date | None
    file_url: str | None
    created_at: datetime
    author_ids: list[uuid.UUID] = Field(default_factory=list)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    funding_source: str | None = Field(default=None, max_length=255)
    status: str = Field(default="ACTIVE", max_length=30)
    start_date: date | None = None
    end_date: date | None = None
    member_ids: list[uuid.UUID] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    funding_source: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, max_length=30)
    start_date: date | None = None
    end_date: date | None = None


class ProjectRead(ProjectCreate, ORMBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    created_at: datetime


class ConferenceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    starts_on: date
    ends_on: date | None = None
    website_url: str | None = Field(default=None, max_length=1000)


class ConferenceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    starts_on: date | None = None
    ends_on: date | None = None
    website_url: str | None = Field(default=None, max_length=1000)


class ConferenceRead(ConferenceCreate, ORMBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    created_at: datetime


class ParticipationCreate(BaseModel):
    conference_id: uuid.UUID
    user_id: uuid.UUID
    presentation_title: str | None = Field(default=None, max_length=500)
    participation_type: str = Field(default="ATTENDEE", max_length=40)


class ParticipationRead(ParticipationCreate, ORMBase):
    id: uuid.UUID
    created_at: datetime


class ConferenceEventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    starts_at: datetime
    ends_at: datetime | None = None
    description: str | None = None


class ConferenceEventRead(ConferenceEventCreate, ORMBase):
    id: uuid.UUID
    conference_id: uuid.UUID
    created_at: datetime


class CollaborationCreate(BaseModel):
    partner_name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: str = Field(default="ACTIVE", max_length=30)


class CollaborationUpdate(BaseModel):
    partner_name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = Field(default=None, max_length=30)


class CollaborationRead(CollaborationCreate, ORMBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    created_at: datetime


class CitationCreate(BaseModel):
    source_publication_id: uuid.UUID
    cited_publication_id: uuid.UUID


class CitationRead(ORMBase):
    id: uuid.UUID
    source_publication_id: uuid.UUID
    cited_publication_id: uuid.UUID
    created_at: datetime


class ProjectAssignmentCreate(BaseModel):
    user_id: uuid.UUID
    role: str = Field(default="MEMBER", min_length=1, max_length=100)


class ProjectAssignmentRead(ProjectAssignmentCreate, ORMBase):
    id: uuid.UUID
    project_id: uuid.UUID


class NotificationRead(ORMBase):
    id: uuid.UUID
    title: str
    message: str
    is_read: bool
    link: str | None
    created_at: datetime


class DashboardSummary(BaseModel):
    researchers: int
    publications: int
    active_projects: int
    conferences: int
    collaborations: int
    citations: int
