from pydantic import BaseModel


class PublicationStatusStats(BaseModel):
    draft: int
    submitted: int
    under_review: int
    revision_required: int
    accepted: int
    rejected: int
    published: int
    archived: int


class SuperAdminDashboard(BaseModel):
    total_publications: int

    publication_status: PublicationStatusStats

    total_institutions: int
    total_researchers: int
    total_reviewers: int


class InstitutionDashboard(BaseModel):
    total_publications: int

    publication_status: PublicationStatusStats

    total_researchers: int
    total_reviewers: int


class ResearcherDashboard(BaseModel):
    my_publications: int

    publication_status: PublicationStatusStats

    coauthored_publications: int


class ReviewerDashboard(BaseModel):
    assigned_reviews: int
    pending_reviews: int
    completed_reviews: int


