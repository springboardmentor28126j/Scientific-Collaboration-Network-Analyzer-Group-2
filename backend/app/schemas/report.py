from pydantic import BaseModel


# ==========================================================
# Dashboard Summary
# ==========================================================

class DashboardSummary(BaseModel):
    total_users: int
    total_researchers: int
    total_institutions: int
    total_publications: int
    total_conferences: int
    total_sessions: int
    total_participations: int
    total_collaborations: int = 0


# ==========================================================
# Institution Reports
# ==========================================================

class InstitutionReport(BaseModel):
    institution_name: str
    researcher_count: int


# ==========================================================
# Publication Reports
# ==========================================================

class PublicationByYearReport(BaseModel):
    year: int | None
    publication_count: int


class PublicationByTypeReport(BaseModel):
    publication_type: str | None
    publication_count: int


class PublicationByStatusReport(BaseModel):
    publication_status: str
    publication_count: int


class ResearcherPublicationReport(BaseModel):
    researcher_id: int
    publication_count: int


# ==========================================================
# Conference Reports
# ==========================================================

class ConferenceTypeReport(BaseModel):
    conference_type: str | None
    conference_count: int


class ConferenceParticipationReport(BaseModel):
    conference_name: str
    participant_count: int


# ==========================================================
# Participation Reports
# ==========================================================

class ParticipationRoleReport(BaseModel):
    role: str
    total: int


class ParticipationStatusReport(BaseModel):
    status: str
    total: int


# ==========================================================
# Session Reports
# ==========================================================

class SessionReport(BaseModel):
    conference_name: str
    total_sessions: int


# ==========================================================
# User Reports
# ==========================================================

class UserRoleReport(BaseModel):
    role: str
    total_users: int


# ==========================================================
# Research Analytics
# ==========================================================

class DepartmentReport(BaseModel):
    department: str | None
    total_researchers: int


class ResearchInterestReport(BaseModel):
    research_interest: str
    total_researchers: int


class SkillReport(BaseModel):
    skill: str
    total_researchers: int


# ==========================================================
# Collaboration Reports
# ==========================================================

class CollaborationRequestStatusReport(BaseModel):
    request_status: str
    request_count: int


class TopCollaborationReport(BaseModel):
    researcher1_email: str
    researcher2_email: str
    strength: int    