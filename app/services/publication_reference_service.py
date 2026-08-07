import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.publication import PublicationStatus
from app.models.publication_reference import PublicationReference
from app.models.publication_reference import PublicationReference
from app.models.user import User
from app.repositories.publication_reference_repository import (
    PublicationReferenceRepository,
)
from app.repositories.publication_repository import PublicationRepository
from app.schemas.publication_reference import (
    PublicationReferenceCreate,
    PublicationReferenceUpdate,
)


class PublicationReferenceService:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.publications = PublicationRepository(session)

        self.references = PublicationReferenceRepository(session)

    async def get_reference(
        self,
        reference_id: uuid.UUID,
    ) -> PublicationReference:
        reference = await self.references.get_by_id(
            reference_id,
        )

        if reference is None:
            raise NotFoundError("Reference not found.")

        return reference

    async def add_reference(
        self,
        publication_id: uuid.UUID,
        payload: PublicationReferenceCreate,
        current_user: User,
    ) -> PublicationReference:
        publication = await self.publications.get_by_id(
            publication_id,
        )

        if publication is None:
            raise NotFoundError("Publication not found.")

        if publication.created_by != current_user.id:
            raise ForbiddenError("You can only add references to your own publication.")

        if publication.status != PublicationStatus.DRAFT:
            raise ConflictError(
                "References can only be modified while the publication is in draft."
            )

        next_order = await self.references.next_reference_order(
            publication.id,
        )

        reference = await self.references.create(
            publication_id=publication.id,
            created_by=current_user.id,
            reference_order=next_order,
            **payload.model_dump(),
        )

        await self.session.commit()

        await self.session.refresh(reference)

        return reference

    async def list_references(
        self,
        publication_id: uuid.UUID,
    ) -> list[PublicationReference]:
        publication = await self.publications.get_by_id(
            publication_id,
        )

        if publication is None:
            raise NotFoundError("Publication not found.")

        return await self.references.list_by_publication(
            publication_id,
        )

    async def update_reference(
        self,
        publication_id: uuid.UUID,
        reference_id: uuid.UUID,
        payload: PublicationReferenceUpdate,
        current_user: User,
    ) -> PublicationReference:
        reference = await self.get_reference(
            reference_id,
        )

        if reference.publication_id != publication_id:
            raise NotFoundError("Reference not found.")

        publication = await self.publications.get_by_id(
            reference.publication_id,
        )

        if publication.created_by != current_user.id:
            raise ForbiddenError("You can only update your own references.")

        if publication.status != PublicationStatus.DRAFT:
            raise ConflictError("Only draft publications can be modified.")

        reference = await self.references.update(
            reference,
            **payload.model_dump(exclude_unset=True),
        )

        await self.session.commit()

        await self.session.refresh(reference)

        return reference

    async def delete_reference(
        self,
        publication_id: uuid.UUID,
        reference_id: uuid.UUID,
        current_user: User,
    ):
        reference = await self.get_reference(
            reference_id,
        )

        if reference.publication_id != publication_id:
            raise NotFoundError("Reference not found.")

        publication = await self.publications.get_by_id(
            reference.publication_id,
        )

        if publication.created_by != current_user.id:
            raise ForbiddenError("You can only delete your own references.")

        if publication.status != PublicationStatus.DRAFT:
            raise ConflictError("Only draft publications can be modified.")

        await self.references.delete(
            reference,
        )

        await self.session.commit()
