from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.audit import log_audit
from app.core.email import send_email
from app.core.notifications import create_notification
from app.db.session import get_db
from app.models.institution import Institution
from app.models.project import Project, ProjectMember, ProjectMemberStatus, ProjectRole
from app.models.researcher import Researcher
from app.models.user import User, UserRole
from app.schemas.project import (
    ProjectCreate,
    ProjectMemberAdd,
    ProjectMemberRespond,
    ProjectOut,
    ProjectUpdate,
)

router = APIRouter()


def _get_current_researcher(db: Session, current_user: User) -> Researcher:
    researcher = db.query(Researcher).filter(Researcher.user_id == current_user.id).first()
    if researcher is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create a researcher profile before creating or joining projects",
        )
    return researcher


def _institution_id_for_admin(db: Session, current_user: User) -> int | None:
    """The single institution an Institution Admin manages, or None if
    they don't manage one yet. Duplicated locally per this codebase's
    existing convention rather than cross-importing between route files."""
    institution = (
        db.query(Institution).filter(Institution.admin_user_id == current_user.id).first()
    )
    return institution.id if institution else None


def _get_project_or_404(db: Session, project_id: int) -> Project:
    project = (
        db.query(Project)
        .options(selectinload(Project.members))
        .filter(Project.id == project_id)
        .first()
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _require_lead_or_admin(project: Project, researcher: Researcher, current_user: User) -> None:
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return
    if project.lead_researcher_id != researcher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project lead or a System Admin can do this",
        )


def _require_view_access(project: Project, researcher: Researcher, current_user: User) -> None:
    """Lead, System Admin, or anyone with a ProjectMember row at all --
    accepted, pending, or declined. Pending is deliberately allowed (a
    real gap in the zip this ports from): a pending invitee has to be
    able to view the project read-only in order to Accept/Decline it."""
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return
    if researcher.id == project.lead_researcher_id:
        return
    if any(m.researcher_id == researcher.id for m in project.members):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not part of this project",
    )


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    researcher = _get_current_researcher(db, current_user)

    data = payload.model_dump()
    if data.get("institution_id") is None:
        data["institution_id"] = researcher.institution_id

    project = Project(**data, lead_researcher_id=researcher.id)
    db.add(project)
    db.flush()

    # The lead never goes through the invite step -- their own
    # membership is created ACCEPTED directly.
    db.add(
        ProjectMember(
            project_id=project.id,
            researcher_id=researcher.id,
            role_in_project=ProjectRole.LEAD,
            status=ProjectMemberStatus.ACCEPTED,
            responded_at=datetime.utcnow(),
        )
    )
    db.commit()
    db.refresh(project)

    log_audit(
        db,
        user_id=current_user.id,
        action="project_created",
        entity_type="project",
        entity_id=project.id,
        details=f"title={project.title!r}",
    )
    return _get_project_or_404(db, project.id)


@router.get("", response_model=list[ProjectOut])
def list_projects(
    status_filter: str | None = None,
    institution_id: int | None = None,
    researcher_id: int | None = None,
    q: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Project]:
    query = db.query(Project).options(selectinload(Project.members))

    if current_user.role == UserRole.SYSTEM_ADMIN:
        # System Admin can see everything, and may still narrow the
        # view with institution_id / researcher_id like before.
        if institution_id is not None:
            query = query.filter(Project.institution_id == institution_id)
        if researcher_id is not None:
            query = query.join(ProjectMember).filter(
                ProjectMember.researcher_id == researcher_id
            )
    elif current_user.role == UserRole.INSTITUTION_ADMIN:
        # Institution Admin sees every project that has at least one
        # ACCEPTED member (or lead, who is always ACCEPTED) belonging to
        # their own institution -- any client-supplied institution_id /
        # researcher_id is ignored so they can't browse other
        # institutions' project lists.
        admin_institution_id = _institution_id_for_admin(db, current_user)
        if admin_institution_id is None:
            return []
        institution_project_ids = (
            db.query(ProjectMember.project_id)
            .join(Researcher, Researcher.id == ProjectMember.researcher_id)
            .filter(
                ProjectMember.status == ProjectMemberStatus.ACCEPTED,
                Researcher.institution_id == admin_institution_id,
            )
            .subquery()
        )
        query = query.filter(Project.id.in_(institution_project_ids))
    else:
        # Every other role only ever sees projects they're an ACCEPTED
        # member (or lead, who is always ACCEPTED) of -- any client-
        # supplied researcher_id/institution_id is ignored here so a
        # researcher can't browse other people's project lists.
        researcher = _get_current_researcher(db, current_user)
        my_project_ids = (
            db.query(ProjectMember.project_id)
            .filter(
                ProjectMember.researcher_id == researcher.id,
                ProjectMember.status == ProjectMemberStatus.ACCEPTED,
            )
            .subquery()
        )
        query = query.filter(Project.id.in_(my_project_ids))

    if status_filter:
        query = query.filter(Project.status == status_filter)
    if q:
        query = query.filter(Project.title.ilike(f"%{q}%"))

    return query.order_by(Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    researcher = _get_current_researcher(db, current_user)
    project = _get_project_or_404(db, project_id)
    _require_view_access(project, researcher, current_user)
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    researcher = _get_current_researcher(db, current_user)
    project = _get_project_or_404(db, project_id)
    _require_lead_or_admin(project, researcher, current_user)

    before_status = project.status.value
    for field, value in payload.model_dump().items():
        setattr(project, field, value)

    db.commit()

    if payload.status.value != before_status:
        log_audit(
            db,
            user_id=current_user.id,
            action="project_updated",
            entity_type="project",
            entity_id=project.id,
            details=f"status: {before_status} -> {payload.status.value}",
        )
    else:
        log_audit(
            db,
            user_id=current_user.id,
            action="project_updated",
            entity_type="project",
            entity_id=project.id,
            details=f"title={project.title!r}",
        )
    return _get_project_or_404(db, project_id)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    researcher = _get_current_researcher(db, current_user)
    project = _get_project_or_404(db, project_id)
    _require_lead_or_admin(project, researcher, current_user)

    title = project.title
    db.delete(project)
    db.commit()

    log_audit(
        db,
        user_id=current_user.id,
        action="project_deleted",
        entity_type="project",
        entity_id=project_id,
        details=f"title={title!r}",
    )


@router.post("/{project_id}/members", response_model=ProjectOut)
def invite_project_member(
    project_id: int,
    payload: ProjectMemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    """Invite a researcher onto the project. This does NOT make them a
    member yet -- it creates a PENDING row and notifies them; they
    become a member only once they accept via respond_to_project_invite."""
    researcher = _get_current_researcher(db, current_user)
    project = _get_project_or_404(db, project_id)
    _require_lead_or_admin(project, researcher, current_user)

    target = db.query(Researcher).filter(Researcher.id == payload.researcher_id).first()
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Researcher not found")

    existing = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.researcher_id == payload.researcher_id,
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This researcher already has an invite or membership on this project",
        )

    db.add(
        ProjectMember(
            project_id=project_id,
            researcher_id=payload.researcher_id,
            role_in_project=payload.role_in_project,
            status=ProjectMemberStatus.PENDING,
            invited_by_id=researcher.id,
        )
    )
    db.commit()

    log_audit(
        db,
        user_id=current_user.id,
        action="project_member_invited",
        entity_type="project",
        entity_id=project_id,
        details=f"researcher_id={payload.researcher_id} role={payload.role_in_project.value}",
    )

    if target.user:
        create_notification(
            db,
            user_id=target.user_id,
            type="project_invite",
            message=f"{current_user.email} invited you to join the project '{project.title}'",
            link_url=f"/projects/{project_id}",
        )
        send_email(
            target.user.email,
            f"You've been invited to '{project.title}'",
            f"{current_user.email} invited you to join the project '{project.title}'. "
            f"Log in to accept or decline the invite.",
        )

    return _get_project_or_404(db, project_id)


@router.post("/{project_id}/members/respond", response_model=ProjectOut)
def respond_to_project_invite(
    project_id: int,
    payload: ProjectMemberRespond,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    """The invitee accepts or declines their own pending invite. Only
    the invite's own owner can respond to it -- looked up by the
    logged-in researcher, not by an id in the URL, so there's no way to
    respond to someone else's invite."""
    researcher = _get_current_researcher(db, current_user)
    project = _get_project_or_404(db, project_id)

    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.researcher_id == researcher.id,
        )
        .first()
    )
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You don't have an invite to this project"
        )
    if member.status != ProjectMemberStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invite has already been responded to",
        )

    member.status = ProjectMemberStatus.ACCEPTED if payload.accept else ProjectMemberStatus.DECLINED
    member.responded_at = datetime.utcnow()
    db.commit()

    log_audit(
        db,
        user_id=current_user.id,
        action="project_invite_responded",
        entity_type="project",
        entity_id=project_id,
        details=member.status.value,
    )

    lead = db.query(Researcher).filter(Researcher.id == project.lead_researcher_id).first()
    if lead and lead.user:
        decision_text = "accepted" if payload.accept else "declined"
        create_notification(
            db,
            user_id=lead.user_id,
            type="project_invite_response",
            message=f"{current_user.email} {decision_text} your invite to '{project.title}'",
            link_url=f"/projects/{project_id}",
        )
        send_email(
            lead.user.email,
            f"Project invite {decision_text}",
            f"{current_user.email} {decision_text} your invite to '{project.title}'.",
        )

    return _get_project_or_404(db, project_id)


@router.delete("/{project_id}/members/{researcher_id}", response_model=ProjectOut)
def remove_project_member(
    project_id: int,
    researcher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    """Also doubles as 'revoke a pending invite' -- works the same way
    regardless of the member's current status."""
    researcher = _get_current_researcher(db, current_user)
    project = _get_project_or_404(db, project_id)
    _require_lead_or_admin(project, researcher, current_user)

    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.researcher_id == researcher_id,
        )
        .first()
    )
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role_in_project == ProjectRole.LEAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't remove the project lead. Update the project to reassign the lead first.",
        )

    db.delete(member)
    db.commit()

    log_audit(
        db,
        user_id=current_user.id,
        action="project_member_removed",
        entity_type="project",
        entity_id=project_id,
        details=f"researcher_id={researcher_id}",
    )
    return _get_project_or_404(db, project_id)
