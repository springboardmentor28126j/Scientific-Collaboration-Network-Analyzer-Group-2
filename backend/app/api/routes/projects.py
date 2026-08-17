from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.api.routes.notifications import create_notification
from app.core.config import settings
from app.core.email import render_email, send_email
from app.core.audit import log_audit
from app.db.session import get_db
from app.models.project import Project, ProjectMember, ProjectMemberRole, ProjectMemberStatus
from app.models.researcher import Researcher
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailOut,
    ProjectMemberAdd,
    ProjectMemberOut,
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
            detail="Create a researcher profile before using projects",
        )
    return researcher


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


def _require_lead(project: Project, researcher: Researcher) -> None:
    if project.lead_researcher_id != researcher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project lead can do this",
        )


def _require_member_of(project: Project, researcher: Researcher) -> None:
    """Allow the lead, accepted members, AND pending invitees to view the
    project — a pending invitee needs to see the page to accept/decline it.
    Actions like editing or removing members still separately check
    _require_lead / accepted-only membership where that matters."""
    if researcher.id == project.lead_researcher_id:
        return
    has_any_membership_row = any(m.researcher_id == researcher.id for m in project.members)
    if not has_any_membership_row:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    researcher = _get_current_researcher(db, current_user)

    project = Project(
        title=payload.title,
        description=payload.description,
        lead_researcher_id=researcher.id,
        institution_id=researcher.institution_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(project)
    db.flush()

    lead_member = ProjectMember(
        project_id=project.id,
        researcher_id=researcher.id,
        role=ProjectMemberRole.LEAD,
        status=ProjectMemberStatus.ACCEPTED,
    )
    db.add(lead_member)
    db.commit()
    db.refresh(project)

    log_audit(db, actor_user_id=current_user.id, action="project_created", entity_type="project", entity_id=project.id, details=project.title)
    return project


@router.get("", response_model=list[ProjectOut])
def list_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    researcher = _get_current_researcher(db, current_user)

    member_project_ids = (
        db.query(ProjectMember.project_id)
        .filter(
            ProjectMember.researcher_id == researcher.id,
            ProjectMember.status == ProjectMemberStatus.ACCEPTED,
        )
        .subquery()
    )

    projects = (
        db.query(Project)
        .filter(Project.id.in_(member_project_ids))
        .order_by(Project.updated_at.desc())
        .all()
    )
    return projects


@router.get("/{project_id}", response_model=ProjectDetailOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    researcher = _get_current_researcher(db, current_user)
    project = _get_project_or_404(db, project_id)
    _require_member_of(project, researcher)
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    researcher = _get_current_researcher(db, current_user)
    project = _get_project_or_404(db, project_id)
    _require_lead(project, researcher)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    log_audit(db, actor_user_id=current_user.id, action="project_updated", entity_type="project", entity_id=project.id)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    researcher = _get_current_researcher(db, current_user)
    project = _get_project_or_404(db, project_id)
    _require_lead(project, researcher)

    log_audit(db, actor_user_id=current_user.id, action="project_deleted", entity_type="project", entity_id=project.id)
    db.delete(project)
    db.commit()


@router.post("/{project_id}/members", response_model=ProjectMemberOut, status_code=status.HTTP_201_CREATED)
def invite_member(
    project_id: int,
    payload: ProjectMemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    researcher = _get_current_researcher(db, current_user)
    project = _get_project_or_404(db, project_id)
    _require_lead(project, researcher)

    existing = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.researcher_id == payload.researcher_id,
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already invited or a member")

    target = db.query(Researcher).filter(Researcher.id == payload.researcher_id).first()
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Researcher not found")

    member = ProjectMember(
        project_id=project_id,
        researcher_id=payload.researcher_id,
        role=ProjectMemberRole.MEMBER,
        status=ProjectMemberStatus.PENDING,
        invited_by_id=researcher.id,
    )
    db.add(member)
    db.commit()
    db.refresh(member)

    if target.user:
        create_notification(
            db,
            recipient_user_id=target.user_id,
            type="project_invite",
            message=f"{current_user.email} invited you to join the project '{project.title}'",
            link=f"/projects/{project_id}",
        )
        send_email(
            to_email=target.user.email,
            subject=f"You've been invited to '{project.title}'",
            html_body=render_email(
                title="Project invitation",
                body_html=f"<p><strong>{current_user.email}</strong> invited you to join the project <strong>{project.title}</strong>.</p>",
                cta_text="View Invite",
                cta_link=f"{settings.FRONTEND_URL}/projects/{project_id}",
            ),
        )

    log_audit(db, actor_user_id=current_user.id, action="project_member_invited", entity_type="project", entity_id=project_id, details=f"researcher_id={member.researcher_id}")
    return member


@router.post("/{project_id}/members/{member_id}/respond", response_model=ProjectMemberOut)
def respond_to_invite(
    project_id: int,
    member_id: int,
    payload: ProjectMemberRespond,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    researcher = _get_current_researcher(db, current_user)
    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.id == member_id, ProjectMember.project_id == project_id)
        .first()
    )
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    if member.researcher_id != researcher.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This invite is not yours")

    from datetime import datetime

    member.status = ProjectMemberStatus.ACCEPTED if payload.accept else ProjectMemberStatus.DECLINED
    member.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(member)

    project = _get_project_or_404(db, project_id)
    lead = db.query(Researcher).filter(Researcher.id == project.lead_researcher_id).first()
    if lead and lead.user:
        decision_text = "accepted" if payload.accept else "declined"
        create_notification(
            db,
            recipient_user_id=lead.user_id,
            type="project_invite_response",
            message=f"{current_user.email} {decision_text} your invite to '{project.title}'",
            link=f"/projects/{project_id}",
        )
        send_email(
            to_email=lead.user.email,
            subject=f"Project invite {decision_text}",
            html_body=render_email(
                title=f"Invite {decision_text}",
                body_html=f"<p><strong>{current_user.email}</strong> {decision_text} your invite to <strong>{project.title}</strong>.</p>",
                cta_text="View Project",
                cta_link=f"{settings.FRONTEND_URL}/projects/{project_id}",
            ),
        )

    log_audit(db, actor_user_id=current_user.id, action="project_invite_responded", entity_type="project", entity_id=project_id, details=member.status.value)
    return member


@router.delete("/{project_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    project_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    researcher = _get_current_researcher(db, current_user)
    project = _get_project_or_404(db, project_id)
    _require_lead(project, researcher)

    member = db.query(ProjectMember).filter(ProjectMember.id == member_id, ProjectMember.project_id == project_id).first()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role == ProjectMemberRole.LEAD:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the project lead")

    log_audit(db, actor_user_id=current_user.id, action="project_member_removed", entity_type="project", entity_id=project_id, details=f"member_id={member_id}")
    db.delete(member)
    db.commit()