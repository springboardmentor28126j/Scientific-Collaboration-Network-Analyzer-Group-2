from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.collaboration import Collaboration
from app.models.project import Project, ProjectMember, ProjectMemberRole, ProjectMemberStatus, ProjectMessage
from app.models.researcher import ResearcherProfile
from app.models.user import User, UserRole
from app.repositories import project_message_repository
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectOut, ProjectMemberOut, ProjectMemberAdd, ProjectMemberRespond,
)
from app.schemas.project_message import ProjectMessageCreate, ProjectMessageOut, ProjectMessageListResponse
from app.utils.audit import write_audit_log
from app.utils.notifications import notify
from app.utils.affiliation import require_verified_affiliation

router = APIRouter(prefix="/projects", tags=["Projects"])


def _get_profile(db: Session, user_id: int) -> ResearcherProfile | None:
    return db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == user_id))


def _are_connected(db: Session, researcher_a_id: int, researcher_b_id: int) -> bool:
    stmt = select(Collaboration).where(
        ((Collaboration.researcher1_id == researcher_a_id) & (Collaboration.researcher2_id == researcher_b_id))
        | ((Collaboration.researcher1_id == researcher_b_id) & (Collaboration.researcher2_id == researcher_a_id))
    )
    return db.scalar(stmt) is not None


def _is_lead(db: Session, current_user: User, project: Project) -> bool:
    profile = _get_profile(db, current_user.user_id)
    return profile is not None and project.lead_researcher_id == profile.researcher_id


def _is_member(db: Session, current_user: User, project: Project) -> bool:
    profile = _get_profile(db, current_user.user_id)
    if profile is None:
        return False
    return db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project.project_id,
            ProjectMember.researcher_id == profile.researcher_id,
            ProjectMember.status == ProjectMemberStatus.ACCEPTED,
        )
    ) is not None


def _is_manager(current_user: User, project: Project) -> bool:
    """System admin, or the institution admin of the project's institution."""
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return True
    return current_user.role == UserRole.INSTITUTION_ADMIN and project.institution_id == current_user.institution_id


def _require_can_manage(db: Session, current_user: User, project: Project) -> None:
    if _is_manager(current_user, project) or _is_lead(db, current_user, project):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only the project lead (or the relevant institution admin / a system admin) can do this",
    )


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(require_roles(UserRole.RESEARCHER, UserRole.INSTITUTION_ADMIN, UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
):
    if payload.end_date and payload.start_date and payload.end_date < payload.start_date:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="end_date cannot be before start_date")

    if current_user.role == UserRole.RESEARCHER:
        require_verified_affiliation(current_user)
        profile = _get_profile(db, current_user.user_id)
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="You need a researcher profile before creating a project"
            )
        lead_researcher_id = profile.researcher_id
        institution_id = current_user.institution_id
    else:
        # Institution/System admin creating on behalf of a researcher.
        if payload.lead_researcher_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="lead_researcher_id is required")
        lead_profile = db.get(ResearcherProfile, payload.lead_researcher_id)
        if lead_profile is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead_researcher_id does not exist")
        lead_user = db.get(User, lead_profile.user_id)
        if current_user.role == UserRole.INSTITUTION_ADMIN and (
            lead_user is None or lead_user.institution_id != current_user.institution_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create projects led by a researcher in your own institution",
            )
        lead_researcher_id = lead_profile.researcher_id
        institution_id = lead_user.institution_id if lead_user else None

    project = Project(
        title=payload.title, description=payload.description,
        start_date=payload.start_date, end_date=payload.end_date,
        lead_researcher_id=lead_researcher_id, institution_id=institution_id,
    )
    db.add(project)
    db.flush()  # get project_id before adding the member row

    db.add(ProjectMember(
        project_id=project.project_id, researcher_id=lead_researcher_id, role=ProjectMemberRole.LEAD,
        status=ProjectMemberStatus.ACCEPTED, responded_at=func.now(),
    ))
    db.commit()
    db.refresh(project)
    write_audit_log(db, current_user.user_id, "CREATE", "project", project.project_id)
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(
    institution_id: int | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    mine: bool = Query(False, description="Only projects I lead or am a member of"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Project)
    if institution_id:
        stmt = stmt.where(Project.institution_id == institution_id)
    if status_filter:
        stmt = stmt.where(Project.status == status_filter)
    if mine:
        profile = _get_profile(db, current_user.user_id)
        if profile is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You don't have a researcher profile yet")
        stmt = stmt.join(ProjectMember, ProjectMember.project_id == Project.project_id).where(
            ProjectMember.researcher_id == profile.researcher_id
        )
    stmt = stmt.order_by(Project.created_at.desc())
    return list(db.scalars(stmt).all())


@router.get("/invitations/pending", response_model=list[ProjectMemberOut])
def list_pending_invitations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Every project invite sent to me that I haven't responded to yet,
    across all projects. Declared before /{project_id} so 'invitations'
    in the URL is never mistaken for a project_id."""
    profile = _get_profile(db, current_user.user_id)
    if profile is None:
        return []
    stmt = select(ProjectMember).where(
        ProjectMember.researcher_id == profile.researcher_id,
        ProjectMember.status == ProjectMemberStatus.PENDING,
    )
    return list(db.scalars(stmt).all())


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _require_can_manage(db, current_user, project)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    write_audit_log(db, current_user.user_id, "UPDATE", "project", project.project_id)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _require_can_manage(db, current_user, project)

    write_audit_log(db, current_user.user_id, "DELETE", "project", project_id)
    db.delete(project)
    db.commit()
    return None


@router.get("/{project_id}/members", response_model=list[ProjectMemberOut])
def list_members(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return list(db.scalars(select(ProjectMember).where(ProjectMember.project_id == project_id)).all())


@router.post("/{project_id}/members", response_model=ProjectMemberOut, status_code=status.HTTP_201_CREATED)
def invite_member(
    project_id: int, payload: ProjectMemberAdd, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Invites a researcher to the project -- creates a PENDING row, not
    an active membership. The invitee must already be connected to the
    project LEAD (not necessarily to whoever is issuing the invite, since
    an institution/system admin managing the project on the lead's behalf
    might not be connected to anyone themselves) -- that's the actual
    enforcement of 'invite connected researchers only'."""
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _require_can_manage(db, current_user, project)

    researcher = db.get(ResearcherProfile, payload.researcher_id)
    if researcher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Researcher not found")

    if payload.researcher_id == project.lead_researcher_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The lead is already on the project")

    if not _are_connected(db, project.lead_researcher_id, payload.researcher_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only invite researchers who are already connected with the project lead",
        )

    existing = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.researcher_id == payload.researcher_id
        )
    )
    if existing is not None:
        if existing.status == ProjectMemberStatus.DECLINED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This researcher already declined an invitation to this project")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This researcher is already invited or on the project")

    inviter_profile = _get_profile(db, current_user.user_id)
    member = ProjectMember(
        project_id=project_id, researcher_id=payload.researcher_id, role=ProjectMemberRole.MEMBER,
        status=ProjectMemberStatus.PENDING,
        invited_by_id=inviter_profile.researcher_id if inviter_profile is not None else None,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    write_audit_log(db, current_user.user_id, "CREATE", "project_member", member.project_member_id)
    if researcher.user_id != current_user.user_id:
        notify(
            db, researcher.user_id, "project_invite", "Project invitation",
            f"You've been invited to join the project \"{project.title}\".",
            link_url=f"/projects/{project.project_id}",
        )
    return member


@router.patch("/{project_id}/members/{project_member_id}/respond", response_model=ProjectMemberOut)
def respond_to_invitation(
    project_id: int, project_member_id: int, payload: ProjectMemberRespond,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    member = db.get(ProjectMember, project_member_id)
    if member is None or member.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    profile = _get_profile(db, current_user.user_id)
    if profile is None or member.researcher_id != profile.researcher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This invitation isn't addressed to you")

    if member.status != ProjectMemberStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This invitation has already been responded to")

    member.status = ProjectMemberStatus.ACCEPTED if payload.accept else ProjectMemberStatus.DECLINED
    member.responded_at = func.now()
    db.commit()
    db.refresh(member)
    write_audit_log(db, current_user.user_id, "UPDATE", "project_member", member.project_member_id)

    project = db.get(Project, project_id)
    lead = db.get(ResearcherProfile, project.lead_researcher_id) if project else None
    if lead is not None:
        verb = "accepted" if payload.accept else "declined"
        notify(
            db, lead.user_id, "project_invite_response", f"Invitation {verb}",
            f"{profile.first_name} {profile.last_name} {verb} your invitation to \"{project.title}\".",
            link_url=f"/projects/{project_id}",
        )
    return member


@router.delete("/{project_id}/members/{researcher_id}", status_code=204)
def remove_member(
    project_id: int, researcher_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.researcher_id == researcher_id
        )
    )
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This researcher is not on the project")

    profile = _get_profile(db, current_user.user_id)
    is_self = profile is not None and profile.researcher_id == researcher_id
    if not is_self:
        _require_can_manage(db, current_user, project)

    if member.role == ProjectMemberRole.LEAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The project lead can't be removed as a member -- delete the project or transfer leadership instead",
        )

    write_audit_log(db, current_user.user_id, "DELETE", "project_member", member.project_member_id)
    db.delete(member)
    db.commit()
    if not is_self:
        removed_researcher = db.get(ResearcherProfile, researcher_id)
        if removed_researcher is not None:
            notify(
                db, removed_researcher.user_id, "project_member_removed", "Removed from a project",
                f"You've been removed from the project \"{project.title}\".",
            )
    return None


# --- Project group chat ---

def _require_accepted_member_or_manager(db: Session, current_user: User, project: Project) -> None:
    if _is_manager(current_user, project) or _is_member(db, current_user, project):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only accepted project members can use this project's group chat",
    )


def _project_message_out(message: ProjectMessage) -> ProjectMessageOut:
    return ProjectMessageOut(
        project_message_id=message.project_message_id,
        project_id=message.project_id,
        sender_id=message.sender_id,
        sender_name=f"{message.sender.first_name} {message.sender.last_name}",
        body=message.body,
        created_at=message.created_at,
    )


@router.post(
    "/{project_id}/messages", response_model=ProjectMessageOut, status_code=status.HTTP_201_CREATED,
)
def send_project_message(
    project_id: int, payload: ProjectMessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _require_accepted_member_or_manager(db, current_user, project)

    profile = _get_profile(db, current_user.user_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You need a researcher profile to post in project chat")

    message = ProjectMessage(project_id=project_id, sender_id=profile.researcher_id, body=payload.body)
    db.add(message)
    db.commit()
    db.refresh(message)
    message = project_message_repository.get_by_id(db, message.project_message_id)
    return _project_message_out(message)


@router.get("/{project_id}/messages", response_model=ProjectMessageListResponse)
def list_project_messages(
    project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _require_accepted_member_or_manager(db, current_user, project)

    messages = project_message_repository.list_thread(db, project_id)
    return ProjectMessageListResponse(items=[_project_message_out(m) for m in messages], total=len(messages))
