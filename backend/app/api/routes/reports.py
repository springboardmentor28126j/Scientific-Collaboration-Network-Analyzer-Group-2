from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func
from fastapi.responses import FileResponse

from app.exports.excel_export import create_dashboard_excel
from app.exports.pdf_export import create_dashboard_pdf

from app.api.deps import get_current_user
from app.db.session import get_db
from collections import Counter

from app.models.user import User
from app.models.researcher import Researcher
from app.models.institution import Institution
from app.models.publication import Publication, PublicationAuthor
from app.models.conference import Conference
from app.models.session import ConferenceSession
from app.models.participation import ConferenceParticipation
from app.models.collaboration import Collaboration, CollaborationRequest

from app.schemas.report import (
    DashboardSummary,
    InstitutionReport,
    PublicationByYearReport,
    PublicationByTypeReport,
    PublicationByStatusReport,
    ResearcherPublicationReport,
    ConferenceTypeReport,
    ConferenceParticipationReport,
    ParticipationRoleReport,
    ParticipationStatusReport,
    SessionReport,
    UserRoleReport,
    DepartmentReport,
    ResearchInterestReport,
    SkillReport,
    CollaborationRequestStatusReport, 
    TopCollaborationReport,
)

router = APIRouter()


def _build_dashboard_summary(db: Session) -> DashboardSummary:
    return DashboardSummary(
        total_users=db.query(User).count(),
        total_researchers=db.query(Researcher).count(),
        total_institutions=db.query(Institution).count(),
        total_publications=db.query(Publication).count(),
        total_conferences=db.query(Conference).count(),
        total_sessions=db.query(ConferenceSession).count(),
        total_participations=db.query(ConferenceParticipation).count(),
        total_collaborations=db.query(Collaboration).count(),
    )


@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns overall statistics for the dashboard."""
    return _build_dashboard_summary(db)


# Dashboard Excel Export API
@router.get("/dashboard/excel")
def export_dashboard_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export dashboard summary as an Excel file."""
    summary = _build_dashboard_summary(db)
    collaboration_status = get_collaboration_request_status_report(db=db, current_user=current_user)
    top_collaborations = get_top_collaborations_report(db=db, current_user=current_user)
    filename = create_dashboard_excel(summary, collaboration_status, top_collaborations)

    return FileResponse(
        path=filename,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# Dashboard PDF Export API
@router.get("/dashboard/pdf")
def export_dashboard_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export dashboard summary as a PDF file."""
    summary = _build_dashboard_summary(db)
    collaboration_status = get_collaboration_request_status_report(db=db, current_user=current_user)
    top_collaborations = get_top_collaborations_report(db=db, current_user=current_user)
    filename = create_dashboard_pdf(summary, collaboration_status, top_collaborations)

    return FileResponse(
        path=filename,
        filename=filename,
        media_type="application/pdf",
    )


# institution
@router.get("/institutions", response_model=list[InstitutionReport])
def get_institution_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the number of researchers in each institution."""
    report = (
        db.query(
            Institution.name.label("institution_name"),
            func.count(Researcher.id).label("researcher_count"),
        )
        .outerjoin(Researcher, Institution.id == Researcher.institution_id)
        .group_by(Institution.id, Institution.name)
        .order_by(Institution.name)
        .all()
    )
    return report


# publications_by_year
@router.get("/publications/year", response_model=list[PublicationByYearReport])
def get_publications_by_year(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the number of publications grouped by publication year."""
    report = (
        db.query(
            Publication.year,
            func.count(Publication.id).label("publication_count"),
        )
        .group_by(Publication.year)
        .order_by(Publication.year.desc())
        .all()
    )
    return report


# Publications by Type
@router.get("/publications/type", response_model=list[PublicationByTypeReport])
def get_publications_by_type(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the number of publications grouped by publication type."""
    report = (
        db.query(
            Publication.type.label("publication_type"),
            func.count(Publication.id).label("publication_count"),
        )
        .group_by(Publication.type)
        .order_by(Publication.type)
        .all()
    )
    return report


# Publications by Status
@router.get("/publications/status", response_model=list[PublicationByStatusReport])
def get_publications_by_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the number of publications grouped by publication status."""
    report = (
        db.query(
            Publication.status.label("publication_status"),
            func.count(Publication.id).label("publication_count"),
        )
        .group_by(Publication.status)
        .order_by(Publication.status)
        .all()
    )
    return report


# Publications by Researcher
@router.get("/publications/researchers", response_model=list[ResearcherPublicationReport])
def get_publications_by_researcher(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the number of publications authored by each researcher."""
    report = (
        db.query(
            PublicationAuthor.researcher_id,
            func.count(PublicationAuthor.publication_id).label("publication_count"),
        )
        .group_by(PublicationAuthor.researcher_id)
        .order_by(PublicationAuthor.researcher_id)
        .all()
    )
    return report


# conferences/type
@router.get("/conferences/type", response_model=list[ConferenceTypeReport])
def get_conference_type_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the number of conferences grouped by conference type."""
    report = (
        db.query(
            Conference.conference_type.label("conference_type"),
            func.count(Conference.id).label("conference_count"),
        )
        .group_by(Conference.conference_type)
        .order_by(Conference.conference_type)
        .all()
    )
    return report


# conferences/participants
@router.get("/conferences/participants", response_model=list[ConferenceParticipationReport])
def get_conference_participation_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the participant count for every conference."""
    report = (
        db.query(
            Conference.name.label("conference_name"),
            func.count(ConferenceParticipation.id).label("participant_count"),
        )
        .outerjoin(ConferenceParticipation, Conference.id == ConferenceParticipation.conference_id)
        .group_by(Conference.id, Conference.name)
        .order_by(Conference.name)
        .all()
    )
    return report


# Participation by Role
@router.get("/participations/roles", response_model=list[ParticipationRoleReport])
def get_participation_role_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the number of conference participations grouped by role."""
    report = (
        db.query(
            ConferenceParticipation.role.label("role"),
            func.count(ConferenceParticipation.id).label("total"),
        )
        .group_by(ConferenceParticipation.role)
        .order_by(ConferenceParticipation.role)
        .all()
    )
    return report


# Participation by Status
@router.get("/participations/status", response_model=list[ParticipationStatusReport])
def get_participation_status_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the number of conference participations grouped by status."""
    report = (
        db.query(
            ConferenceParticipation.status.label("status"),
            func.count(ConferenceParticipation.id).label("total"),
        )
        .group_by(ConferenceParticipation.status)
        .order_by(ConferenceParticipation.status)
        .all()
    )
    return report


# session report
@router.get("/sessions", response_model=list[SessionReport])
def get_session_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the number of sessions scheduled for each conference."""
    report = (
        db.query(
            Conference.name.label("conference_name"),
            func.count(ConferenceSession.id).label("total_sessions"),
        )
        .outerjoin(ConferenceSession, Conference.id == ConferenceSession.conference_id)
        .group_by(Conference.id, Conference.name)
        .order_by(Conference.name)
        .all()
    )
    return report


# UserRoleReport
@router.get("/users/roles", response_model=list[UserRoleReport])
def get_user_role_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the number of users grouped by role."""
    report = (
        db.query(
            User.role.label("role"),
            func.count(User.id).label("total_users"),
        )
        .group_by(User.role)
        .order_by(User.role)
        .all()
    )
    return report


# department report
@router.get("/departments", response_model=list[DepartmentReport])
def get_department_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns number of researchers in each department."""
    report = (
        db.query(
            Researcher.department.label("department"),
            func.count(Researcher.id).label("total_researchers"),
        )
        .group_by(Researcher.department)
        .order_by(Researcher.department)
        .all()
    )
    return report


# Research Interest Analytics
@router.get("/research-interests", response_model=list[ResearchInterestReport])
def get_research_interest_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns most common research interests."""
    researchers = db.query(Researcher).all()
    counter = Counter()

    for researcher in researchers:
        if researcher.research_interests:
            interests = [i.strip() for i in researcher.research_interests.split(",")]
            counter.update(interests)

    return [
        {"research_interest": interest, "total_researchers": count}
        for interest, count in counter.most_common()
    ]


# skill analytics
@router.get("/skills", response_model=list[SkillReport])
def get_skill_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns most common researcher skills."""
    researchers = db.query(Researcher).all()
    counter = Counter()

    for researcher in researchers:
        if researcher.skills:
            skills = [s.strip() for s in researcher.skills.split(",")]
            counter.update(skills)

    return [
        {"skill": skill, "total_researchers": count}
        for skill, count in counter.most_common()
    ]


@router.get("/collaborations/status", response_model=list[CollaborationRequestStatusReport])
def get_collaboration_request_status_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the count of collaboration requests grouped by status
    (pending / accepted / rejected / cancelled)."""
    report = (
        db.query(
            CollaborationRequest.status.label("request_status"),
            func.count(CollaborationRequest.id).label("request_count"),
        )
        .group_by(CollaborationRequest.status)
        .all()
    )
    return [
        CollaborationRequestStatusReport(request_status=row.request_status.value, request_count=row.request_count)
        for row in report
    ]


@router.get("/collaborations/top", response_model=list[TopCollaborationReport])
def get_top_collaborations_report(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the strongest collaborations (most shared publications),
    highest strength first."""
    r1 = aliased(Researcher)
    r2 = aliased(Researcher)
    u1 = aliased(User)
    u2 = aliased(User)

    report = (
        db.query(
            u1.email.label("researcher1_email"),
            u2.email.label("researcher2_email"),
            Collaboration.strength,
        )
        .join(r1, Collaboration.researcher1_id == r1.id)
        .join(r2, Collaboration.researcher2_id == r2.id)
        .join(u1, r1.user_id == u1.id)
        .join(u2, r2.user_id == u2.id)
        .order_by(Collaboration.strength.desc())
        .limit(limit)
        .all()
    )
    return [TopCollaborationReport(**row._mapping) for row in report]   