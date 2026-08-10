from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.audit import log_audit
from app.core.email import send_email
from app.core.notifications import create_notification
from app.db.session import get_db
from app.models.project import Project, ProjectMember, ProjectRole
from app.models.researcher import Researcher
from app.models.user import User, UserRole
from app.schemas.project import (
    ProjectCreate,
    ProjectMemberAdd,
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

    db.add(
        ProjectMember(
            project_id=project.id,
            researcher_id=researcher.id,
            role_in_project=ProjectRole.LEAD,
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
    db: Session = Depends(get_db),
) -> list[Project]:
    query = db.query(Project).options(selectinload(Project.members))
    if status_filter:
        query = query.filter(Project.status == status_filter)
    if institution_id is not None:
        query = query.filter(Project.institution_id == institution_id)
    if q:
        query = query.filter(Project.title.ilike(f"%{q}%"))
    if researcher_id is not None:
        query = query.join(ProjectMember).filter(
            ProjectMember.researcher_id == researcher_id
        )
    return query.order_by(Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)) -> Project:
    return _get_project_or_404(db, project_id)


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
def add_project_member(
    project_id: int,
    payload: ProjectMemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
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
            detail="This researcher is already a member of the project",
        )

    db.add(
        ProjectMember(
            project_id=project_id,
            researcher_id=payload.researcher_id,
            role_in_project=payload.role_in_project,
        )
    )
    db.commit()

    log_audit(
        db,
        user_id=current_user.id,
        action="project_member_added",
        entity_type="project",
        entity_id=project_id,
        details=f"researcher_id={payload.researcher_id} role={payload.role_in_project.value}",
    )

    create_notification(
        db,
        user_id=target.user_id,
        type="project_member_added",
        message=(
            f"You were added to the project '{project.title}' "
            f"as {payload.role_in_project.value}"
        ),
        link_url=f"/projects/{project_id}",
    )
    if target.user:
        send_email(
            target.user.email,
            "Added to a research project",
            f"You were added to the project '{project.title}' as {payload.role_in_project.value}.",
        )

    return _get_project_or_404(db, project_id)


@router.delete("/{project_id}/members/{researcher_id}", response_model=ProjectOut)
def remove_project_member(
    project_id: int,
    researcher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
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
