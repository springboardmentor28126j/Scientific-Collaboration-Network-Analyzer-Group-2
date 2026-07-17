import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.publication import PublicationStatus
from app.models.publication_history import PublicationHistoryAction
from app.models.user import User, UserRole
from app.repositories.publication_conference_repository import (
    PublicationConferenceRepository,
)
from app.repositories.publication_repository import PublicationRepository
from app.schemas.publication_conference import (
    PublicationConferenceCreate,
    PublicationConferenceUpdate,
)
from app.services.publication_history_service import PublicationHistoryService


class PublicationConferenceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.publications = PublicationRepository(session)
        self.conferences = PublicationConferenceRepository(session)
        self.history = PublicationHistoryService(session)
    
    async def create_conference(
        self,
        publication_id: uuid.UUID,
        payload: PublicationConferenceCreate,
        current_user: User,
    ):
        if current_user.role != UserRole.SUPER_ADMIN:
            raise ForbiddenError(
                "Only the super administrator can create conference details."
            )
        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")
        
        if publication.status != PublicationStatus.PUBLISHED:
            raise ConflictError(
                "Conference details can only be added to published publications."
            )
        existing = await self.conferences.get_by_publication(publication_id)

        if existing:
            raise ConflictError(
                "Conference details already exist for this publication."
            )
        conference = await self.conferences.create(
            publication_id=publication.id,
            created_by=current_user.id,
            **payload.model_dump(),
        )

        await self.history.log(
            publication_id=publication.id,
            performed_by=current_user.id,
            action=PublicationHistoryAction.CONFERENCE_CREATED,
            description="Conference details added.",
        )
        await self.session.commit()
        await self.session.refresh(conference)

        return conference
    
    async def get_conference(
        self,
        publication_id: uuid.UUID,
    ):
        conference = await self.conferences.get_by_publication(publication_id)

        if conference is None:
            raise NotFoundError(
                "Conference details not found."
            )

        return conference
    
    async def update_conference(
        self,
        publication_id: uuid.UUID,
        payload: PublicationConferenceUpdate,
        current_user: User,
    ):
        if current_user.role != UserRole.SUPER_ADMIN:
            raise ForbiddenError(
                "Only the super administrator can update conference details."
            )

        conference = await self.get_conference(publication_id)

        update_data = payload.model_dump(exclude_unset=True)

        conference = await self.conferences.update(
            conference,
            **update_data,
        )

        await self.history.log(
            publication_id=publication_id,
            performed_by=current_user.id,
            action=PublicationHistoryAction.CONFERENCE_UPDATED,
            description="Conference details updated.",
        )

        await self.session.commit()
        await self.session.refresh(conference)

        return conference