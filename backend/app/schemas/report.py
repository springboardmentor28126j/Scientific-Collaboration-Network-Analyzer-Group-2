from datetime import date, datetime

from pydantic import BaseModel


class LabeledCount(BaseModel):
    """Generic 'this many of that' row -- reused for every by_status /
    by_type / by_role / by_recommendation breakdown across all 8 reports,
    rather than a bespoke schema per breakdown."""
    label: str
    count: int


class PublicationBrief(BaseModel):
    publication_id: int
    title: str
    publication_type: str
    status: str
    year: int | None
    publication_date: date | None
    venue_name: str | None


class ProjectBrief(BaseModel):
    project_id: int
    title: str
    status: str
    start_date: date | None
    end_date: date | None


class ConferenceBrief(BaseModel):
    conference_id: int
    name: str
    status: str
    start_date: date | None
    end_date: date | None
    location: str | None


class ReviewBrief(BaseModel):
    review_id: int
    target_type: str
    status: str
    recommendation: str | None
    assigned_at: datetime
    reviewer_name: str | None = None


class CollaboratorBrief(BaseModel):
    collaboration_id: int
    researcher_id: int
    name: str
    academic_title: str | None
    institution_name: str | None
    strength: int
    first_collaboration: date | None
    last_collaboration: date | None


class ResearcherBrief(BaseModel):
    user_id: int
    name: str
    email: str
    is_active: bool
    is_approved: bool


# --- Report response shapes -----------------------------------------------

class ResearcherReportOut(BaseModel):
    researcher_id: int
    name: str
    publication_count: int
    project_count: int
    collaboration_count: int
    review_count: int
    publications_by_status: list[LabeledCount]
    publications_by_type: list[LabeledCount]
    publications: list[PublicationBrief]
    projects: list[ProjectBrief]
    collaborations: list[CollaboratorBrief]
    reviews: list[ReviewBrief]


class InstitutionReportOut(BaseModel):
    institution_id: int
    institution_name: str
    total_researchers: int
    approved_researchers: int
    pending_researchers: int
    total_departments: int
    total_publications: int
    total_projects: int
    total_conferences: int
    researchers: list[ResearcherBrief]
    publications: list[PublicationBrief]
    projects: list[ProjectBrief]
    conferences: list[ConferenceBrief]


class PublicationsReportOut(BaseModel):
    total: int
    by_status: list[LabeledCount]
    by_type: list[LabeledCount]
    items: list[PublicationBrief]


class ProjectsReportOut(BaseModel):
    total: int
    by_status: list[LabeledCount]
    items: list[ProjectBrief]


class ConferencesReportOut(BaseModel):
    total: int
    by_status: list[LabeledCount]
    items: list[ConferenceBrief]


class ReviewsReportOut(BaseModel):
    scope: str  # "mine" (reviewer's own assignments) or "all" (system-wide, system_admin only)
    total: int
    completed: int
    by_status: list[LabeledCount]
    by_recommendation: list[LabeledCount]
    items: list[ReviewBrief]


class CollaborationsReportOut(BaseModel):
    total_collaborators: int
    total_strength: int
    items: list[CollaboratorBrief]


class SystemReportOut(BaseModel):
    total_users: int
    users_by_role: list[LabeledCount]
    total_institutions: int
    total_publications: int
    publications_by_status: list[LabeledCount]
    total_projects: int
    projects_by_status: list[LabeledCount]
    total_conferences: int
    conferences_by_status: list[LabeledCount]
    total_reviewers: int
