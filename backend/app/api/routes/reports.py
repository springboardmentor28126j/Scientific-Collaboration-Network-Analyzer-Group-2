from datetime import date, datetime, timedelta
import os

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, aliased, selectinload
from sqlalchemy import func
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.exports.excel_export import create_compliance_excel, create_dashboard_excel
from app.exports.pdf_export import create_compliance_pdf, create_dashboard_pdf

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from collections import Counter

from app.models.user import User, UserRole
from app.models.researcher import Researcher
from app.models.institution import Institution
from app.models.publication import Publication, PublicationAuthor
from app.models.citation import Citation
from app.models.conference import Conference
from app.models.session import ConferenceSession
from app.models.participation import ConferenceParticipation
from app.models.audit_log import AuditLog
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
    TopCitedPublicationReport,
    InfluentialPublicationReport,
    TopCitedResearcherReport,
    TopCitedInstitutionReport,
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
def export_dashboard_excel(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    summary = _build_dashboard_summary(db)
    filename = create_dashboard_excel(
        summary,
        collaboration_status=get_collaboration_request_status_report(db=db, current_user=current_user),
        top_collaborations=get_top_collaborations_report(db=db, current_user=current_user),
        institution_report=get_institution_report(db=db, current_user=current_user),
        publication_year=get_publications_by_year(db=db, current_user=current_user),
        publication_type=get_publications_by_type(db=db, current_user=current_user),
        publication_status=get_publications_by_status(db=db, current_user=current_user),
        conference_type=get_conference_type_report(db=db, current_user=current_user),
        user_roles=get_user_role_report(db=db, current_user=current_user),
        departments=get_department_report(db=db, current_user=current_user),
        interests=get_research_interest_report(db=db, current_user=current_user),
        skills=get_skill_report(db=db, current_user=current_user),
    )
    return FileResponse(
        path=filename,
        filename="dashboard_report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        background=BackgroundTask(os.remove, filename),
    )


# Dashboard PDF Export API
@router.get("/dashboard/pdf")
def export_dashboard_pdf(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    summary = _build_dashboard_summary(db)
    filename = create_dashboard_pdf(
        summary,
        collaboration_status=get_collaboration_request_status_report(db=db, current_user=current_user),
        top_collaborations=get_top_collaborations_report(db=db, current_user=current_user),
        institution_report=get_institution_report(db=db, current_user=current_user),
        publication_year=get_publications_by_year(db=db, current_user=current_user),
        publication_type=get_publications_by_type(db=db, current_user=current_user),
        publication_status=get_publications_by_status(db=db, current_user=current_user),
        conference_type=get_conference_type_report(db=db, current_user=current_user),
        user_roles=get_user_role_report(db=db, current_user=current_user),
        departments=get_department_report(db=db, current_user=current_user),
        interests=get_research_interest_report(db=db, current_user=current_user),
        skills=get_skill_report(db=db, current_user=current_user),
    )
    return FileResponse(
        path=filename,
        filename="dashboard_report.pdf",
        media_type="application/pdf",
        background=BackgroundTask(os.remove, filename),
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


# ==========================================================
# Citation Analytics
# ==========================================================
# Adapted from the reference project's analytics_repository.py, remapped
# onto this project's own Citation/Publication/PublicationAuthor models.
# Every citation row here has citing_publication_id set (always internal)
# and cited_publication_id set ONLY when the cited work is also in our
# database -- citations of external/outside works (cited_title instead)
# don't count toward anyone's "times cited" score, since we have no
# publication_id to attribute them to.

def _cited_counts_subquery(db: Session):
    """publication_id -> how many times it has been cited by another
    publication in this system. Reused by all four queries below."""
    return (
        db.query(
            Citation.cited_publication_id.label("publication_id"),
            func.count(Citation.id).label("cnt"),
        )
        .filter(Citation.cited_publication_id.isnot(None))
        .group_by(Citation.cited_publication_id)
        .subquery()
    )


@router.get("/citations/top-papers", response_model=list[TopCitedPublicationReport])
def get_top_cited_publications_report(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """'Frequently referenced' -- raw incoming citation count, most cited first."""
    counts = _cited_counts_subquery(db)
    rows = (
        db.query(Publication.id, Publication.title, counts.c.cnt)
        .join(counts, counts.c.publication_id == Publication.id)
        .order_by(counts.c.cnt.desc())
        .limit(limit)
        .all()
    )
    return [
        TopCitedPublicationReport(publication_id=pid, title=title, citation_count=cnt)
        for pid, title, cnt in rows
    ]


@router.get("/citations/influential-papers", response_model=list[InfluentialPublicationReport])
def get_influential_publications_report(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """'Most influential' -- a citation from a paper that is itself
    highly-cited counts more than one from an uncited paper. One-hop
    weighted score: score(P) = sum over each citation P receives of
    (1 + citation_count of the paper doing the citing)."""
    counts = _cited_counts_subquery(db)
    citing_pub = aliased(Publication)
    rows = (
        db.query(
            Publication.id,
            Publication.title,
            func.sum(1 + func.coalesce(counts.c.cnt, 0)).label("influence_score"),
        )
        .join(Citation, Citation.cited_publication_id == Publication.id)
        .join(citing_pub, citing_pub.id == Citation.citing_publication_id)
        .outerjoin(counts, counts.c.publication_id == citing_pub.id)
        .group_by(Publication.id, Publication.title)
        .order_by(func.sum(1 + func.coalesce(counts.c.cnt, 0)).desc())
        .limit(limit)
        .all()
    )
    return [
        InfluentialPublicationReport(publication_id=pid, title=title, influence_score=int(score))
        for pid, title, score in rows
    ]


@router.get("/citations/top-researchers", response_model=list[TopCitedResearcherReport])
def get_top_cited_researchers_report(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Most cited researcher -- citations summed across every publication
    where they're a listed author."""
    counts = _cited_counts_subquery(db)
    rows = (
        db.query(
            PublicationAuthor.researcher_id,
            func.coalesce(func.sum(counts.c.cnt), 0).label("total_citations"),
            func.count(func.distinct(PublicationAuthor.publication_id)).label("publication_count"),
        )
        .outerjoin(counts, counts.c.publication_id == PublicationAuthor.publication_id)
        .group_by(PublicationAuthor.researcher_id)
        .order_by(func.coalesce(func.sum(counts.c.cnt), 0).desc())
        .limit(limit)
        .all()
    )

    researcher_ids = [r.researcher_id for r in rows]
    if not researcher_ids:
        return []
    researchers = {
        r.id: r for r in db.query(Researcher).options(selectinload(Researcher.user)).filter(Researcher.id.in_(researcher_ids)).all()
    }
    results = []
    for row in rows:
        researcher = researchers.get(row.researcher_id)
        if researcher is None:
            continue
        name = researcher.user.email if researcher.user else f"Researcher #{researcher.id}"
        results.append(
            TopCitedResearcherReport(
                researcher_id=researcher.id,
                name=name,
                total_citations=int(row.total_citations),
                publication_count=int(row.publication_count),
            )
        )
    return results


@router.get("/citations/top-institutions", response_model=list[TopCitedInstitutionReport])
def get_top_cited_institutions_report(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Institution with the highest research impact -- total citations
    across all its researchers' publications, plus citations-per-publication
    so a small institution with a few highly-cited papers isn't buried
    under one that simply publishes more volume."""
    counts = _cited_counts_subquery(db)
    rows = (
        db.query(
            Researcher.institution_id,
            func.coalesce(func.sum(counts.c.cnt), 0).label("total_citations"),
            func.count(func.distinct(Publication.id)).label("publication_count"),
        )
        .join(PublicationAuthor, PublicationAuthor.researcher_id == Researcher.id)
        .join(Publication, Publication.id == PublicationAuthor.publication_id)
        .outerjoin(counts, counts.c.publication_id == Publication.id)
        .filter(Researcher.institution_id.isnot(None))
        .group_by(Researcher.institution_id)
        .order_by(func.coalesce(func.sum(counts.c.cnt), 0).desc())
        .limit(limit)
        .all()
    )

    institution_ids = [r.institution_id for r in rows]
    if not institution_ids:
        return []
    institutions = {i.id: i for i in db.query(Institution).filter(Institution.id.in_(institution_ids)).all()}
    results = []
    for row in rows:
        institution = institutions.get(row.institution_id)
        if institution is None:
            continue
        total = int(row.total_citations)
        pub_count = int(row.publication_count)
        results.append(
            TopCitedInstitutionReport(
                institution_id=institution.id,
                name=institution.name,
                total_citations=total,
                publication_count=pub_count,
                avg_citations_per_publication=round(total / pub_count, 2) if pub_count else 0.0,
            )
        )
    return results


@router.get("/compliance")
def get_compliance_report(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """A period-bounded snapshot: publication decisions, login failures, and
    account-level admin actions. Defaults to the last 30 days."""
    if end_date is None:
        end_date = datetime.utcnow().date()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.created_at >= start_dt, AuditLog.created_at <= end_dt)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    publication_decisions = [l for l in logs if l.action in ("publication_approved", "publication_rejected")]
    login_failures = [l for l in logs if l.action == "login_failed"]
    mfa_events = [l for l in logs if l.action in ("mfa_enabled", "mfa_disabled", "mfa_failed")]
    account_admin_actions = [
        l for l in logs
        if l.action in ("user_registered", "institution_admin_applied", "password_reset_completed")
    ]

    return {
        "period": {"start": str(start_date), "end": str(end_date)},
        "totals": {
            "publication_decisions": len(publication_decisions),
            "login_failures": len(login_failures),
            "mfa_events": len(mfa_events),
            "account_admin_actions": len(account_admin_actions),
        },
        "publication_decisions": [
            {"date": str(l.created_at), "action": l.action, "actor_email": l.actor.email if l.actor else None, "details": l.details}
            for l in publication_decisions
        ],
        "login_failures": [
            {"date": str(l.created_at), "attempted_email": l.details} for l in login_failures
        ],
        "mfa_events": [
            {"date": str(l.created_at), "action": l.action, "actor_email": l.actor.email if l.actor else None}
            for l in mfa_events
        ],
    }


@router.get("/compliance/excel")
def export_compliance_excel(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SYSTEM_ADMIN)),
):
    report = get_compliance_report(start_date=start_date, end_date=end_date, db=db, current_user=current_user)
    filename = create_compliance_excel(report)
    return FileResponse(
        path=filename,
        filename="compliance_report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        background=BackgroundTask(os.remove, filename),
    )


@router.get("/compliance/pdf")
def export_compliance_pdf(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SYSTEM_ADMIN)),
):
    report = get_compliance_report(start_date=start_date, end_date=end_date, db=db, current_user=current_user)
    filename = create_compliance_pdf(report)
    return FileResponse(
        path=filename,
        filename="compliance_report.pdf",
        media_type="application/pdf",
        background=BackgroundTask(os.remove, filename),
    )   