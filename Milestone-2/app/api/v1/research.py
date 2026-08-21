import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_institution_admin
from app.db.session import get_session
from app.models.research import (
    Citation,
    Conference,
    ConferenceEvent,
    ConferenceParticipation,
    InstitutionalCollaboration,
    Notification,
    Project,
    ProjectMember,
    Publication,
    PublicationAuthor,
    ResearcherProfile,
)
from app.models.institution import Institution
from app.models.user import User, UserRole
from app.schemas.research import (
    CitationCreate,
    CitationRead,
    CollaborationCreate,
    CollaborationRead,
    CollaborationUpdate,
    ConferenceCreate,
    ConferenceRead,
    ConferenceUpdate,
    ConferenceEventCreate,
    ConferenceEventRead,
    DashboardSummary,
    NotificationRead,
    ParticipationCreate,
    ParticipationRead,
    ProjectAssignmentCreate,
    ProjectAssignmentRead,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    PublicationCreate,
    PublicationRead,
    PublicationStatus,
    PublicationType,
    PublicationUpdate,
    ResearcherProfileRead,
    ResearcherProfileUpdate,
)
from app.services.cloudinary_service import CloudinaryService

router = APIRouter(prefix="/research", tags=["Research management"])


def institution_id_for(user: User) -> uuid.UUID:
    if user.institution_id is None:
        raise HTTPException(status_code=400, detail="Select an institution-scoped account")
    return user.institution_id


async def owned_members(session: AsyncSession, institution_id: uuid.UUID, user_ids: list[uuid.UUID]) -> None:
    if not user_ids:
        return
    count = await session.scalar(
        select(func.count())
        .select_from(User)
        .where(User.id.in_(set(user_ids)), User.institution_id == institution_id)
    )
    if count != len(set(user_ids)):
        raise HTTPException(status_code=422, detail="All selected users must belong to your institution")


async def notify_users(
    session: AsyncSession, user_ids: Sequence[uuid.UUID], title: str, message: str, link: str | None = None
) -> None:
    session.add_all(
        Notification(user_id=user_id, title=title, message=message, link=link)
        for user_id in set(user_ids)
    )


async def institution_member_ids(session: AsyncSession, institution_id: uuid.UUID) -> list[uuid.UUID]:
    return list((await session.scalars(select(User.id).where(User.institution_id == institution_id))).all())


async def publication_read(session: AsyncSession, publication: Publication) -> PublicationRead:
    author_ids = list(
        (await session.scalars(
            select(PublicationAuthor.user_id)
            .where(PublicationAuthor.publication_id == publication.id)
            .order_by(PublicationAuthor.author_order)
        )).all()
    )
    return PublicationRead.model_validate(publication, from_attributes=True).model_copy(
        update={"author_ids": author_ids}
    )


async def get_publication(session: AsyncSession, publication_id: uuid.UUID, institution_id: uuid.UUID) -> Publication:
    publication = await session.scalar(
        select(Publication).where(Publication.id == publication_id, Publication.institution_id == institution_id)
    )
    if publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    return publication


async def ensure_publication_editor(
    session: AsyncSession, publication: Publication, user: User
) -> None:
    if user.role == UserRole.INSTITUTION_ADMIN:
        return
    is_author = await session.scalar(
        select(PublicationAuthor.id).where(
            PublicationAuthor.publication_id == publication.id, PublicationAuthor.user_id == user.id
        )
    )
    if is_author is None:
        raise HTTPException(status_code=403, detail="Only a publication author or institution admin may modify it")


@router.get("/profile", response_model=ResearcherProfileRead)
async def get_profile(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> ResearcherProfile:
    profile = await session.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == user.id))
    if profile is None:
        profile = ResearcherProfile(user_id=user.id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
    return profile


@router.put("/profile", response_model=ResearcherProfileRead)
async def update_profile(payload: ResearcherProfileUpdate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> ResearcherProfile:
    profile = await session.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == user.id))
    if profile is None:
        profile = ResearcherProfile(user_id=user.id)
        session.add(profile)
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    await session.commit()
    await session.refresh(profile)
    return profile


@router.get("/search")
async def global_search(
    query: str = Query(min_length=2, max_length=100),
    limit: int = Query(default=6, ge=1, le=20),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, str]]:
    match = f"%{query.strip()}%"
    results: list[dict[str, str]] = []

    def append(kind: str, item_id: uuid.UUID, title: str, subtitle: str, path: str) -> None:
        results.append({"type": kind, "id": str(item_id), "title": title, "subtitle": subtitle, "path": path})

    if user.role == UserRole.SUPER_ADMIN:
        institutions = list((await session.scalars(select(Institution).where(Institution.name.ilike(match)).limit(limit))).all())
        for institution in institutions:
            append("Institution", institution.id, institution.name, institution.address, "/dashboard/institutions")
        researchers = list((await session.scalars(select(User).where(User.role == UserRole.RESEARCHER, or_(User.full_name.ilike(match), User.email.ilike(match))).limit(limit))).all())
        for researcher in researchers:
            append("Researcher", researcher.id, researcher.full_name, researcher.email, "/dashboard/researchers")
        return results[: limit * 2]

    institution_id = institution_id_for(user)
    institution = await session.scalar(select(Institution).where(Institution.id == institution_id, Institution.name.ilike(match)))
    if institution:
        append("Institution", institution.id, institution.name, institution.address, "/dashboard/profile")

    researchers = list((await session.scalars(select(User).where(User.institution_id == institution_id, User.role == UserRole.RESEARCHER, or_(User.full_name.ilike(match), User.email.ilike(match))).limit(limit))).all())
    for researcher in researchers:
        append("Researcher", researcher.id, researcher.full_name, researcher.email, "/dashboard/users")

    publications = list((await session.scalars(select(Publication).where(Publication.institution_id == institution_id, or_(Publication.title.ilike(match), Publication.abstract.ilike(match), Publication.doi.ilike(match))).limit(limit))).all())
    for publication in publications:
        append("Publication", publication.id, publication.title, publication.status, "/dashboard/publications")

    conferences = list((await session.scalars(select(Conference).where(Conference.institution_id == institution_id, or_(Conference.name.ilike(match), Conference.location.ilike(match))).limit(limit))).all())
    for conference in conferences:
        append("Conference", conference.id, conference.name, conference.location or "Conference", "/dashboard/conferences")

    projects = list((await session.scalars(select(Project).where(Project.institution_id == institution_id, or_(Project.name.ilike(match), Project.description.ilike(match))).limit(limit))).all())
    for project in projects:
        append("Project", project.id, project.name, project.status, "/dashboard/projects")

    return results[: limit * 5]


@router.get("/publications", response_model=list[PublicationRead])
async def list_publications(
    query: str | None = Query(default=None, min_length=1, max_length=200),
    publication_type: PublicationType | None = None,
    publication_status: PublicationStatus | None = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[PublicationRead]:
    statement = select(Publication).where(Publication.institution_id == institution_id_for(user))
    if query:
        match = f"%{query.strip()}%"
        statement = statement.where(or_(Publication.title.ilike(match), Publication.abstract.ilike(match), Publication.doi.ilike(match)))
    if publication_type:
        statement = statement.where(Publication.publication_type == publication_type)
    if publication_status:
        statement = statement.where(Publication.status == publication_status)
    publications = list((await session.scalars(statement.order_by(Publication.created_at.desc()))).all())
    return [await publication_read(session, publication) for publication in publications]


@router.post("/publications", response_model=PublicationRead, status_code=status.HTTP_201_CREATED)
async def create_publication(payload: PublicationCreate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> PublicationRead:
    institution_id = institution_id_for(user)
    author_ids = list(dict.fromkeys(payload.author_ids or [user.id]))
    await owned_members(session, institution_id, author_ids)
    publication = Publication(institution_id=institution_id, **payload.model_dump(exclude={"author_ids"}))
    session.add(publication)
    await session.flush()
    session.add_all(
        PublicationAuthor(publication_id=publication.id, user_id=author_id, author_order=index + 1)
        for index, author_id in enumerate(author_ids)
    )
    await notify_users(session, author_ids, "Publication created", f"{publication.title} was added to the research workspace.", "/dashboard/research-management")
    await session.commit()
    await session.refresh(publication)
    return await publication_read(session, publication)


@router.get("/publications/{publication_id}", response_model=PublicationRead)
async def read_publication(publication_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> PublicationRead:
    return await publication_read(session, await get_publication(session, publication_id, institution_id_for(user)))


@router.patch("/publications/{publication_id}", response_model=PublicationRead)
async def update_publication(publication_id: uuid.UUID, payload: PublicationUpdate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> PublicationRead:
    publication = await get_publication(session, publication_id, institution_id_for(user))
    await ensure_publication_editor(session, publication, user)
    values = payload.model_dump(exclude_unset=True, exclude={"author_ids"})
    for field, value in values.items():
        setattr(publication, field, value)
    if payload.author_ids is not None:
        author_ids = list(dict.fromkeys(payload.author_ids))
        await owned_members(session, institution_id_for(user), author_ids)
        await session.execute(delete(PublicationAuthor).where(PublicationAuthor.publication_id == publication.id))
        session.add_all(
            PublicationAuthor(publication_id=publication.id, user_id=author_id, author_order=index + 1)
            for index, author_id in enumerate(author_ids)
        )
    author_ids = list((await session.scalars(select(PublicationAuthor.user_id).where(PublicationAuthor.publication_id == publication.id))).all())
    await notify_users(session, author_ids, "Publication updated", f"{publication.title} was updated.", "/dashboard/research-management")
    await session.commit()
    await session.refresh(publication)
    return await publication_read(session, publication)


@router.delete("/publications/{publication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(publication_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> None:
    publication = await get_publication(session, publication_id, institution_id_for(user))
    await ensure_publication_editor(session, publication, user)
    await session.delete(publication)
    await session.commit()


@router.post("/publications/{publication_id}/file", response_model=PublicationRead)
async def upload_publication_file(publication_id: uuid.UUID, file: UploadFile = File(...), user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> PublicationRead:
    publication = await get_publication(session, publication_id, institution_id_for(user))
    await ensure_publication_editor(session, publication, user)
    if not file.filename:
        raise HTTPException(status_code=422, detail="Choose a file to upload")
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Publication attachments must be PDF files")
    url, _public_id = await CloudinaryService.upload_publication_file(file)
    publication.file_url = url
    await session.commit()
    await session.refresh(publication)
    return await publication_read(session, publication)


@router.get("/projects", response_model=list[ProjectRead])
async def list_projects(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> list[ProjectRead]:
    projects = list((await session.scalars(select(Project).where(Project.institution_id == institution_id_for(user)).order_by(Project.created_at.desc()))).all())
    result = []
    for project in projects:
        member_ids = list((await session.scalars(select(ProjectMember.user_id).where(ProjectMember.project_id == project.id))).all())
        result.append(ProjectRead.model_validate(project, from_attributes=True).model_copy(update={"member_ids": member_ids}))
    return result


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> ProjectRead:
    institution_id = institution_id_for(user)
    await owned_members(session, institution_id, payload.member_ids)
    project = Project(institution_id=institution_id, **payload.model_dump(exclude={"member_ids"}))
    session.add(project)
    await session.flush()
    session.add_all(ProjectMember(project_id=project.id, user_id=member_id) for member_id in set(payload.member_ids))
    await notify_users(session, payload.member_ids, "Project assignment", f"You were added to project: {project.name}.", "/dashboard/research-management")
    await session.commit()
    await session.refresh(project)
    return ProjectRead.model_validate(project, from_attributes=True).model_copy(update={"member_ids": payload.member_ids})


async def get_project(session: AsyncSession, project_id: uuid.UUID, institution_id: uuid.UUID) -> Project:
    project = await session.scalar(select(Project).where(Project.id == project_id, Project.institution_id == institution_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/projects/{project_id}", response_model=ProjectRead)
async def update_project(project_id: uuid.UUID, payload: ProjectUpdate, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> ProjectRead:
    project = await get_project(session, project_id, institution_id_for(user))
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await session.commit()
    await session.refresh(project)
    member_ids = list((await session.scalars(select(ProjectMember.user_id).where(ProjectMember.project_id == project.id))).all())
    return ProjectRead.model_validate(project, from_attributes=True).model_copy(update={"member_ids": member_ids})


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: uuid.UUID, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> None:
    await session.delete(await get_project(session, project_id, institution_id_for(user)))
    await session.commit()


@router.get("/projects/{project_id}/assignments", response_model=list[ProjectAssignmentRead])
async def list_project_assignments(project_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Sequence[ProjectMember]:
    await get_project(session, project_id, institution_id_for(user))
    return (await session.scalars(select(ProjectMember).where(ProjectMember.project_id == project_id))).all()


@router.post("/projects/{project_id}/assignments", response_model=ProjectAssignmentRead, status_code=status.HTTP_201_CREATED)
async def create_project_assignment(project_id: uuid.UUID, payload: ProjectAssignmentCreate, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> ProjectMember:
    project = await get_project(session, project_id, institution_id_for(user))
    await owned_members(session, project.institution_id, [payload.user_id])
    existing = await session.scalar(select(ProjectMember).where(ProjectMember.project_id == project.id, ProjectMember.user_id == payload.user_id))
    if existing:
        existing.role = payload.role
        assignment = existing
    else:
        assignment = ProjectMember(project_id=project.id, **payload.model_dump())
        session.add(assignment)
    await notify_users(session, [payload.user_id], "Project assignment", f"You were assigned to project: {project.name}.", "/dashboard/research-management")
    await session.commit()
    await session.refresh(assignment)
    return assignment


@router.delete("/projects/{project_id}/assignments/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_assignment(project_id: uuid.UUID, user_id: uuid.UUID, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> None:
    await get_project(session, project_id, institution_id_for(user))
    assignment = await session.scalar(select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id))
    if assignment is None:
        raise HTTPException(status_code=404, detail="Project assignment not found")
    await session.delete(assignment)
    await session.commit()


@router.get("/conferences", response_model=list[ConferenceRead])
async def list_conferences(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Sequence[Conference]:
    return (await session.scalars(select(Conference).where(Conference.institution_id == institution_id_for(user)).order_by(Conference.starts_on.desc()))).all()


@router.post("/conferences", response_model=ConferenceRead, status_code=status.HTTP_201_CREATED)
async def create_conference(payload: ConferenceCreate, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> Conference:
    conference = Conference(institution_id=institution_id_for(user), **payload.model_dump())
    session.add(conference)
    await session.commit()
    await session.refresh(conference)
    return conference


async def get_conference(session: AsyncSession, conference_id: uuid.UUID, institution_id: uuid.UUID) -> Conference:
    conference = await session.scalar(select(Conference).where(Conference.id == conference_id, Conference.institution_id == institution_id))
    if conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return conference


@router.patch("/conferences/{conference_id}", response_model=ConferenceRead)
async def update_conference(conference_id: uuid.UUID, payload: ConferenceUpdate, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> Conference:
    conference = await get_conference(session, conference_id, institution_id_for(user))
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(conference, field, value)
    await session.commit()
    await session.refresh(conference)
    return conference


@router.delete("/conferences/{conference_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conference(conference_id: uuid.UUID, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> None:
    await session.delete(await get_conference(session, conference_id, institution_id_for(user)))
    await session.commit()


@router.post("/conference-participations", status_code=status.HTTP_201_CREATED)
async def add_participation(payload: ParticipationCreate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    institution_id = institution_id_for(user)
    await get_conference(session, payload.conference_id, institution_id)
    await owned_members(session, institution_id, [payload.user_id])
    session.add(ConferenceParticipation(**payload.model_dump()))
    await session.commit()
    return {"detail": "Participation recorded"}


@router.get("/conferences/{conference_id}/participations", response_model=list[ParticipationRead])
async def list_participations(conference_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Sequence[ConferenceParticipation]:
    await get_conference(session, conference_id, institution_id_for(user))
    return (await session.scalars(select(ConferenceParticipation).where(ConferenceParticipation.conference_id == conference_id).order_by(ConferenceParticipation.created_at.desc()))).all()


@router.get("/conferences/{conference_id}/events", response_model=list[ConferenceEventRead])
async def list_conference_events(conference_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Sequence[ConferenceEvent]:
    await get_conference(session, conference_id, institution_id_for(user))
    return (await session.scalars(select(ConferenceEvent).where(ConferenceEvent.conference_id == conference_id).order_by(ConferenceEvent.starts_at))).all()


@router.post("/conferences/{conference_id}/events", response_model=ConferenceEventRead, status_code=status.HTTP_201_CREATED)
async def create_conference_event(conference_id: uuid.UUID, payload: ConferenceEventCreate, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> ConferenceEvent:
    await get_conference(session, conference_id, institution_id_for(user))
    event = ConferenceEvent(conference_id=conference_id, **payload.model_dump())
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


@router.delete("/conferences/{conference_id}/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conference_event(conference_id: uuid.UUID, event_id: uuid.UUID, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> None:
    await get_conference(session, conference_id, institution_id_for(user))
    event = await session.scalar(select(ConferenceEvent).where(ConferenceEvent.id == event_id, ConferenceEvent.conference_id == conference_id))
    if event is None:
        raise HTTPException(status_code=404, detail="Conference event not found")
    await session.delete(event)
    await session.commit()


@router.get("/collaborations", response_model=list[CollaborationRead])
async def list_collaborations(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Sequence[InstitutionalCollaboration]:
    return (await session.scalars(select(InstitutionalCollaboration).where(InstitutionalCollaboration.institution_id == institution_id_for(user)))).all()


@router.post("/collaborations", response_model=CollaborationRead, status_code=status.HTTP_201_CREATED)
async def create_collaboration(payload: CollaborationCreate, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> InstitutionalCollaboration:
    institution_id = institution_id_for(user)
    collaboration = InstitutionalCollaboration(institution_id=institution_id, **payload.model_dump())
    session.add(collaboration)
    await notify_users(
        session,
        await institution_member_ids(session, institution_id),
        "Collaboration created",
        f"A collaboration with {collaboration.partner_name} was added to your institution.",
        "/dashboard/collaborations",
    )
    await session.commit()
    await session.refresh(collaboration)
    return collaboration


async def get_collaboration(session: AsyncSession, collaboration_id: uuid.UUID, institution_id: uuid.UUID) -> InstitutionalCollaboration:
    collaboration = await session.scalar(select(InstitutionalCollaboration).where(InstitutionalCollaboration.id == collaboration_id, InstitutionalCollaboration.institution_id == institution_id))
    if collaboration is None:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    return collaboration


@router.patch("/collaborations/{collaboration_id}", response_model=CollaborationRead)
async def update_collaboration(collaboration_id: uuid.UUID, payload: CollaborationUpdate, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> InstitutionalCollaboration:
    collaboration = await get_collaboration(session, collaboration_id, institution_id_for(user))
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(collaboration, field, value)
    await notify_users(
        session,
        await institution_member_ids(session, collaboration.institution_id),
        "Collaboration updated",
        f"The collaboration with {collaboration.partner_name} was updated.",
        "/dashboard/collaborations",
    )
    await session.commit()
    await session.refresh(collaboration)
    return collaboration


@router.delete("/collaborations/{collaboration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collaboration(collaboration_id: uuid.UUID, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)) -> None:
    await session.delete(await get_collaboration(session, collaboration_id, institution_id_for(user)))
    await session.commit()


@router.get("/citations", response_model=list[CitationRead])
async def list_citations(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Sequence[Citation]:
    institution_id = institution_id_for(user)
    return (await session.scalars(
        select(Citation).join(Publication, Publication.id == Citation.source_publication_id).where(Publication.institution_id == institution_id)
    )).all()


@router.post("/citations", response_model=CitationRead, status_code=status.HTTP_201_CREATED)
async def create_citation(payload: CitationCreate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Citation:
    institution_id = institution_id_for(user)
    publications = list((await session.scalars(select(Publication).where(Publication.id.in_([payload.source_publication_id, payload.cited_publication_id]), Publication.institution_id == institution_id))).all())
    if len(publications) != 2 or payload.source_publication_id == payload.cited_publication_id:
        raise HTTPException(status_code=422, detail="Choose two different publications in your institution")
    citation = Citation(**payload.model_dump())
    session.add(citation)
    await session.commit()
    await session.refresh(citation)
    return citation


@router.delete("/citations/{citation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_citation(citation_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> None:
    citation = await session.scalar(
        select(Citation).join(Publication, Publication.id == Citation.source_publication_id).where(Citation.id == citation_id, Publication.institution_id == institution_id_for(user))
    )
    if citation is None:
        raise HTTPException(status_code=404, detail="Citation not found")
    await session.delete(citation)
    await session.commit()


@router.get("/notifications", response_model=list[NotificationRead])
async def list_notifications(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Sequence[Notification]:
    return (await session.scalars(select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc()))).all()


@router.patch("/notifications/{notification_id}/read", response_model=NotificationRead)
async def mark_notification_read(notification_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Notification:
    notification = await session.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user.id))
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    await session.commit()
    await session.refresh(notification)
    return notification


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> None:
    notification = await session.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user.id))
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    await session.delete(notification)
    await session.commit()


@router.get("/dashboard", response_model=DashboardSummary)
async def dashboard(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> DashboardSummary:
    institution_id = institution_id_for(user)

    async def count(model, *conditions):
        return await session.scalar(select(func.count()).select_from(model).where(*conditions)) or 0

    return DashboardSummary(
        researchers=await count(User, User.institution_id == institution_id, User.role == UserRole.RESEARCHER),
        publications=await count(Publication, Publication.institution_id == institution_id),
        active_projects=await count(Project, Project.institution_id == institution_id, Project.status == "ACTIVE"),
        conferences=await count(Conference, Conference.institution_id == institution_id),
        collaborations=await count(InstitutionalCollaboration, InstitutionalCollaboration.institution_id == institution_id),
        citations=await session.scalar(select(func.count()).select_from(Citation).join(Publication, Publication.id == Citation.source_publication_id).where(Publication.institution_id == institution_id)) or 0,
    )


@router.get("/analytics")
async def analytics(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> dict:
    institution_id = institution_id_for(user)
    publications = list((await session.scalars(select(Publication).where(Publication.institution_id == institution_id))).all())
    profiles = list((await session.execute(select(ResearcherProfile.department).join(User, User.id == ResearcherProfile.user_id).where(User.institution_id == institution_id))).scalars())
    years: dict[str, int] = {}
    for publication in publications:
        year = str(publication.published_on.year if publication.published_on else publication.created_at.year)
        years[year] = years.get(year, 0) + 1
    departments: dict[str, int] = {}
    for department in profiles:
        key = department or "Unassigned"
        departments[key] = departments.get(key, 0) + 1
    collaborations = await session.scalar(select(func.count()).select_from(InstitutionalCollaboration).where(InstitutionalCollaboration.institution_id == institution_id)) or 0
    conferences = await session.scalar(select(func.count()).select_from(Conference).where(Conference.institution_id == institution_id)) or 0
    projects = await session.scalar(select(func.count()).select_from(Project).where(Project.institution_id == institution_id)) or 0
    researchers = await session.scalar(select(func.count()).select_from(User).where(User.institution_id == institution_id, User.role == UserRole.RESEARCHER)) or 0
    recent = [{"title": publication.title, "type": "Publication", "date": publication.created_at.isoformat()} for publication in sorted(publications, key=lambda item: item.created_at, reverse=True)[:5]]
    return {"cards": {"researchers": researchers, "publications": len(publications), "conferences": conferences, "projects": projects, "collaborations": collaborations}, "publications_per_year": [{"year": year, "count": count} for year, count in sorted(years.items())], "publications_by_department": [{"department": department, "count": count} for department, count in departments.items()], "collaboration_statistics": [{"name": "Collaborations", "value": collaborations}, {"name": "Projects", "value": projects}], "institution_statistics": [{"name": "Researchers", "value": researchers}, {"name": "Conferences", "value": conferences}], "recent_activity": recent}
