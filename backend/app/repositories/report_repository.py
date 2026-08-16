from datetime import date

from sqlalchemy import select, func, or_, exists
from sqlalchemy.orm import Session

from app.models.collaboration import Collaboration
from app.models.conference import Conference, ConferenceParticipation
from app.models.institution import Institution, Department
from app.models.project import Project, ProjectMember
from app.models.publication import Publication, PublicationAuthor
from app.models.researcher import ResearcherProfile
from app.models.review import Review
from app.models.user import User, UserRole, AffiliationStatus


# --- Brief-row builders -----------------------------------------------
# Plain dicts, not the Pydantic schema classes themselves -- the endpoint
# layer wraps these into PublicationBrief/etc. Keeping this layer schema-
# agnostic means the repository has no FastAPI/Pydantic import at all.

def _pub_brief(p: Publication) -> dict:
    return dict(
        publication_id=p.publication_id, title=p.title, publication_type=p.publication_type.value,
        status=p.status.value, year=p.publication_date.year if p.publication_date else None,
        publication_date=p.publication_date, venue_name=p.venue_name,
    )


def _project_brief(p: Project) -> dict:
    return dict(
        project_id=p.project_id, title=p.title, status=p.status.value,
        start_date=p.start_date, end_date=p.end_date,
    )


def _conference_brief(c: Conference) -> dict:
    return dict(
        conference_id=c.conference_id, name=c.name, status=c.status.value,
        start_date=c.start_date, end_date=c.end_date, location=c.location,
    )


def _review_brief(r: Review) -> dict:
    return dict(
        review_id=r.review_id, target_type=r.target_type.value, status=r.status.value,
        recommendation=r.recommendation.value if r.recommendation else None, assigned_at=r.assigned_at,
    )


def _institution_name_for(db: Session, profile: ResearcherProfile) -> str | None:
    """A researcher's institution lives on User.institution_id, not on
    ResearcherProfile itself -- this mirrors that indirection so callers
    don't have to re-derive it."""
    user = db.get(User, profile.user_id)
    if user is None or user.institution_id is None:
        return None
    institution = db.get(Institution, user.institution_id)
    return institution.name if institution else None


def _grouped_counts(rows) -> list[dict]:
    """rows: iterable of (enum_or_value, count) from a GROUP BY query."""
    return [{"label": (v.value if hasattr(v, "value") else str(v)), "count": c} for v, c in rows]


# --- Researcher report ---------------------------------------------------

def researcher_report(db: Session, profile: ResearcherProfile, is_reviewer: bool) -> dict:
    pubs = list(db.scalars(select(Publication).where(Publication.primary_author_id == profile.researcher_id)).all())
    pub_status_rows = db.execute(
        select(Publication.status, func.count()).where(Publication.primary_author_id == profile.researcher_id)
        .group_by(Publication.status)
    ).all()
    pub_type_rows = db.execute(
        select(Publication.publication_type, func.count()).where(Publication.primary_author_id == profile.researcher_id)
        .group_by(Publication.publication_type)
    ).all()

    projects = list(
        db.scalars(
            select(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.project_id)
            .where(ProjectMember.researcher_id == profile.researcher_id)
            .order_by(Project.created_at.desc())
        ).all()
    )

    collaborations = list(
        db.scalars(
            select(Collaboration).where(
                or_(Collaboration.researcher1_id == profile.researcher_id, Collaboration.researcher2_id == profile.researcher_id)
            )
        ).all()
    )
    collab_briefs = []
    for c in collaborations:
        other_id = c.researcher2_id if c.researcher1_id == profile.researcher_id else c.researcher1_id
        other = db.get(ResearcherProfile, other_id)
        collab_briefs.append(dict(
            collaboration_id=c.collaboration_id, researcher_id=other_id,
            name=f"{other.first_name} {other.last_name}" if other else "Unknown",
            academic_title=other.academic_title if other else None,
            institution_name=_institution_name_for(db, other) if other else None,
            strength=c.strength, first_collaboration=c.first_collaboration, last_collaboration=c.last_collaboration,
        ))

    reviews = []
    if is_reviewer:
        reviews = list(
            db.scalars(select(Review).where(Review.reviewer_id == profile.user_id).order_by(Review.assigned_at.desc())).all()
        )

    return dict(
        researcher_id=profile.researcher_id, name=f"{profile.first_name} {profile.last_name}",
        publication_count=len(pubs), project_count=len(projects), collaboration_count=len(collaborations),
        review_count=len(reviews),
        publications_by_status=_grouped_counts(pub_status_rows), publications_by_type=_grouped_counts(pub_type_rows),
        publications=[_pub_brief(p) for p in pubs], projects=[_project_brief(p) for p in projects],
        collaborations=collab_briefs, reviews=[_review_brief(r) for r in reviews],
    )


# --- Institution report ----------------------------------------------------

def institution_report(db: Session, institution: Institution) -> dict:
    institution_id = institution.institution_id

    total_researchers = db.scalar(
        select(func.count()).select_from(User).where(User.institution_id == institution_id, User.role == UserRole.RESEARCHER)
    )
    approved_researchers = db.scalar(
        select(func.count()).select_from(User).where(
            User.institution_id == institution_id, User.role == UserRole.RESEARCHER,
            User.affiliation_status == AffiliationStatus.APPROVED,
        )
    )
    pending_researchers = db.scalar(
        select(func.count()).select_from(User).where(
            User.institution_id == institution_id, User.role == UserRole.RESEARCHER,
            User.affiliation_status == AffiliationStatus.PENDING,
        )
    )
    total_departments = db.scalar(select(func.count()).select_from(Department).where(Department.institution_id == institution_id))

    researcher_users = list(
        db.scalars(select(User).where(User.institution_id == institution_id, User.role == UserRole.RESEARCHER)).all()
    )
    researcher_briefs = []
    for u in researcher_users:
        profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == u.user_id))
        name = f"{profile.first_name} {profile.last_name}" if profile else u.email
        researcher_briefs.append(dict(
            user_id=u.user_id, name=name, email=u.email, is_active=u.is_active,
            is_approved=u.affiliation_status == AffiliationStatus.APPROVED,
        ))

    publications = list(db.scalars(select(Publication).where(Publication.institution_id == institution_id)).all())
    projects = list(db.scalars(select(Project).where(Project.institution_id == institution_id)).all())
    conferences = list(db.scalars(select(Conference).where(Conference.organizing_institution_id == institution_id)).all())

    return dict(
        institution_id=institution_id, institution_name=institution.name,
        total_researchers=total_researchers or 0, approved_researchers=approved_researchers or 0,
        pending_researchers=pending_researchers or 0, total_departments=total_departments or 0,
        total_publications=len(publications), total_projects=len(projects), total_conferences=len(conferences),
        researchers=researcher_briefs, publications=[_pub_brief(p) for p in publications],
        projects=[_project_brief(p) for p in projects], conferences=[_conference_brief(c) for c in conferences],
    )


# --- Publications report ----------------------------------------------------

def publications_report(db: Session, researcher_id: int | None = None, year: int | None = None) -> dict:
    stmt = select(Publication)
    status_stmt = select(Publication.status, func.count())
    type_stmt = select(Publication.publication_type, func.count())

    if researcher_id is not None:
        stmt = stmt.where(Publication.primary_author_id == researcher_id)
        status_stmt = status_stmt.where(Publication.primary_author_id == researcher_id)
        type_stmt = type_stmt.where(Publication.primary_author_id == researcher_id)
    if year is not None:
        stmt = stmt.where(Publication.publication_date >= date(year, 1, 1), Publication.publication_date < date(year + 1, 1, 1))
        status_stmt = status_stmt.where(Publication.publication_date >= date(year, 1, 1), Publication.publication_date < date(year + 1, 1, 1))
        type_stmt = type_stmt.where(Publication.publication_date >= date(year, 1, 1), Publication.publication_date < date(year + 1, 1, 1))

    items = list(db.scalars(stmt).all())
    by_status = db.execute(status_stmt.group_by(Publication.status)).all()
    by_type = db.execute(type_stmt.group_by(Publication.publication_type)).all()

    return dict(
        total=len(items), by_status=_grouped_counts(by_status), by_type=_grouped_counts(by_type),
        items=[_pub_brief(p) for p in items],
    )


# --- Projects report ----------------------------------------------------

def projects_report(db: Session, researcher_id: int | None = None) -> dict:
    stmt = select(Project)
    status_stmt = select(Project.status, func.count())

    if researcher_id is not None:
        # Matches list_projects()'s mine= semantics exactly: lead OR member,
        # including still-pending invitations (same as the existing endpoint).
        member_join = select(ProjectMember.project_id).where(ProjectMember.researcher_id == researcher_id)
        stmt = stmt.where(Project.project_id.in_(member_join))
        status_stmt = status_stmt.where(Project.project_id.in_(member_join))

    items = list(db.scalars(stmt).all())
    by_status = db.execute(status_stmt.group_by(Project.status)).all()

    return dict(total=len(items), by_status=_grouped_counts(by_status), items=[_project_brief(p) for p in items])


# --- Conferences report ----------------------------------------------------

def conferences_report(db: Session, researcher_id: int | None = None) -> dict:
    stmt = select(Conference)
    status_stmt = select(Conference.status, func.count())

    if researcher_id is not None:
        participant_exists = exists(
            select(1).select_from(ConferenceParticipation).where(
                ConferenceParticipation.conference_id == Conference.conference_id,
                ConferenceParticipation.researcher_id == researcher_id,
            )
        )
        stmt = stmt.where(participant_exists)
        status_stmt = status_stmt.where(participant_exists)

    items = list(db.scalars(stmt).all())
    by_status = db.execute(status_stmt.group_by(Conference.status)).all()

    return dict(total=len(items), by_status=_grouped_counts(by_status), items=[_conference_brief(c) for c in items])


# --- Reviews report (own assignments, or system-wide for system_admin) ----

def reviews_report(db: Session, reviewer_user_id: int) -> dict:
    items = list(
        db.scalars(select(Review).where(Review.reviewer_id == reviewer_user_id).order_by(Review.assigned_at.desc())).all()
    )
    by_status = db.execute(
        select(Review.status, func.count()).where(Review.reviewer_id == reviewer_user_id).group_by(Review.status)
    ).all()
    by_recommendation = db.execute(
        select(Review.recommendation, func.count())
        .where(Review.reviewer_id == reviewer_user_id, Review.recommendation.isnot(None))
        .group_by(Review.recommendation)
    ).all()
    completed = sum(1 for r in items if r.status.value == "completed")

    return dict(
        scope="mine", total=len(items), completed=completed, by_status=_grouped_counts(by_status),
        by_recommendation=_grouped_counts(by_recommendation), items=[_review_brief(r) for r in items],
    )


def _reviewer_display_name(db: Session, reviewer_user_id: int) -> str:
    """Reviewers may or may not have a ResearcherProfile -- fall back to
    their account email when they don't, so the system-wide reviews report
    always has something readable in the Reviewer column."""
    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == reviewer_user_id))
    if profile:
        return f"{profile.first_name} {profile.last_name}"
    user = db.get(User, reviewer_user_id)
    return user.email if user else "Unknown"


def all_reviews_report(db: Session) -> dict:
    """System-wide view across every reviewer's assignments -- for
    system_admin oversight, since a system_admin account has no reviews
    of its own to report on."""
    items = list(db.scalars(select(Review).order_by(Review.assigned_at.desc())).all())
    by_status = db.execute(select(Review.status, func.count()).group_by(Review.status)).all()
    by_recommendation = db.execute(
        select(Review.recommendation, func.count()).where(Review.recommendation.isnot(None)).group_by(Review.recommendation)
    ).all()
    completed = sum(1 for r in items if r.status.value == "completed")

    briefs = []
    for r in items:
        brief = _review_brief(r)
        brief["reviewer_name"] = _reviewer_display_name(db, r.reviewer_id)
        briefs.append(brief)

    return dict(
        scope="all", total=len(items), completed=completed, by_status=_grouped_counts(by_status),
        by_recommendation=_grouped_counts(by_recommendation), items=briefs,
    )


# --- Collaborations report ----------------------------------------------

def collaborations_report(db: Session, researcher_id: int) -> dict:
    collaborations, _total = _all_collaborations_for(db, researcher_id)
    items = []
    total_strength = 0
    for c in collaborations:
        other_id = c.researcher2_id if c.researcher1_id == researcher_id else c.researcher1_id
        other = db.get(ResearcherProfile, other_id)
        total_strength += c.strength
        items.append(dict(
            collaboration_id=c.collaboration_id, researcher_id=other_id,
            name=f"{other.first_name} {other.last_name}" if other else "Unknown",
            academic_title=other.academic_title if other else None,
            institution_name=_institution_name_for(db, other) if other else None,
            strength=c.strength, first_collaboration=c.first_collaboration, last_collaboration=c.last_collaboration,
        ))
    return dict(total_collaborators=len(items), total_strength=total_strength, items=items)


def _all_collaborations_for(db: Session, researcher_id: int):
    stmt = select(Collaboration).where(
        or_(Collaboration.researcher1_id == researcher_id, Collaboration.researcher2_id == researcher_id)
    )
    items = list(db.scalars(stmt).all())
    return items, len(items)


# --- System report (system admin only) ------------------------------------

def system_report(db: Session) -> dict:
    role_rows = db.execute(select(User.role, func.count()).group_by(User.role)).all()
    total_users = sum(c for _, c in role_rows)
    total_reviewers = next((c for r, c in role_rows if r == UserRole.REVIEWER), 0)

    total_institutions = db.scalar(select(func.count()).select_from(Institution))

    pub_rows = db.execute(select(Publication.status, func.count()).group_by(Publication.status)).all()
    total_publications = sum(c for _, c in pub_rows)

    proj_rows = db.execute(select(Project.status, func.count()).group_by(Project.status)).all()
    total_projects = sum(c for _, c in proj_rows)

    conf_rows = db.execute(select(Conference.status, func.count()).group_by(Conference.status)).all()
    total_conferences = sum(c for _, c in conf_rows)

    return dict(
        total_users=total_users, users_by_role=_grouped_counts(role_rows),
        total_institutions=total_institutions or 0,
        total_publications=total_publications, publications_by_status=_grouped_counts(pub_rows),
        total_projects=total_projects, projects_by_status=_grouped_counts(proj_rows),
        total_conferences=total_conferences, conferences_by_status=_grouped_counts(conf_rows),
        total_reviewers=total_reviewers,
    )
