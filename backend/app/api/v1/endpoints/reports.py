from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.institution import Institution
from app.models.researcher import ResearcherProfile
from app.models.user import User, UserRole
from app.repositories import report_repository as repo
from app.schemas.report import (
    ResearcherReportOut, InstitutionReportOut, PublicationsReportOut, ProjectsReportOut,
    ConferencesReportOut, ReviewsReportOut, CollaborationsReportOut, SystemReportOut,
)

router = APIRouter(prefix="/reports", tags=["Reports"])


def _my_profile_or_400(db: Session, current_user: User) -> ResearcherProfile:
    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You don't have a researcher profile yet")
    return profile


@router.get("/researcher", response_model=ResearcherReportOut)
def researcher_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Always the current user's own report -- there's no researcher_id
    param here on purpose. An admin who wants someone else's activity
    should use the institution report, which is explicitly scoped for
    oversight; this endpoint is a personal summary, not a lookup tool."""
    profile = _my_profile_or_400(db, current_user)
    data = repo.researcher_report(db, profile, is_reviewer=current_user.role == UserRole.REVIEWER)
    return ResearcherReportOut(**data)


@router.get("/institution/{institution_id}", response_model=InstitutionReportOut)
def institution_report(
    institution_id: int,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.INSTITUTION_ADMIN and current_user.institution_id != institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another institution's report")

    institution = db.get(Institution, institution_id)
    if institution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    data = repo.institution_report(db, institution)
    return InstitutionReportOut(**data)


@router.get("/publications", response_model=PublicationsReportOut)
def publications_report(
    mine: bool = Query(False, description="Only publications where I'm the primary author"),
    year: int | None = Query(None, description="Only publications dated in this year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    researcher_id = _my_profile_or_400(db, current_user).researcher_id if mine else None
    return PublicationsReportOut(**repo.publications_report(db, researcher_id=researcher_id, year=year))


@router.get("/projects", response_model=ProjectsReportOut)
def projects_report(
    mine: bool = Query(False, description="Only projects I lead or am a member of"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    researcher_id = _my_profile_or_400(db, current_user).researcher_id if mine else None
    return ProjectsReportOut(**repo.projects_report(db, researcher_id=researcher_id))


@router.get("/conferences", response_model=ConferencesReportOut)
def conferences_report(
    mine: bool = Query(False, description="Only conferences I'm registered for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    researcher_id = _my_profile_or_400(db, current_user).researcher_id if mine else None
    return ConferencesReportOut(**repo.conferences_report(db, researcher_id=researcher_id))


@router.get("/reviews", response_model=ReviewsReportOut)
def reviews_report(
    current_user: User = Depends(require_roles(UserRole.REVIEWER, UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    A Reviewer sees their own assignments (mirrors /reviews/mine exactly).
    A System Admin has no review assignments of their own, so they get the
    system-wide view across every reviewer instead -- that's the
    meaningful "all reports" access for this report type. Institution Admin
    is intentionally excluded: reviews aren't scoped to an institution, and
    the data call behind this always required an actual account with
    reviews to show (a reviewer's own, or literally all of them).
    """
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return ReviewsReportOut(**repo.all_reviews_report(db))
    return ReviewsReportOut(**repo.reviews_report(db, current_user.user_id))


@router.get("/collaborations", response_model=CollaborationsReportOut)
def collaborations_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = _my_profile_or_400(db, current_user)
    return CollaborationsReportOut(**repo.collaborations_report(db, profile.researcher_id))


@router.get("/system", response_model=SystemReportOut)
def system_report(
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
):
    return SystemReportOut(**repo.system_report(db))
