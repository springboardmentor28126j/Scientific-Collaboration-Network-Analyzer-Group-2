import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.publication import PublicationStatus
from app.models.publication_author import PublicationAuthor
from app.models.user import User, UserRole
from app.repositories.publication_author_repository import PublicationAuthorRepository
from app.repositories.publication_repository import PublicationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.publication_author import PublicationAuthorCreate, PublicationAuthorRead
from app.models.publication_history import PublicationHistoryAction
from app.services.publication_history_service import PublicationHistoryService


class PublicationAuthorService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.publications = PublicationRepository(session)
        self.authors = PublicationAuthorRepository(session)
        self.users = UserRepository(session)
        self.history = PublicationHistoryService(session)

    def _to_read_schema(self, author: PublicationAuthor) -> PublicationAuthorRead:
        return PublicationAuthorRead(
            researcher_id=author.researcher_id,
            full_name=author.researcher.full_name,
            institution=(
                author.researcher.institution.name if author.researcher.institution else None
            ),
            author_order=author.author_order,
            is_corresponding_author=author.is_corresponding_author,
        )

    async def add_author(
        self,
        publication_id: uuid.UUID,
        payload: PublicationAuthorCreate,
        current_user: User,
    ) -> PublicationAuthor:

        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        if publication.created_by != current_user.id:
            raise ForbiddenError("Only the publication owner can manage authors.")

        if publication.status != PublicationStatus.DRAFT:
            raise ConflictError("Authors can only be modified while the publication is in DRAFT.")

        researcher = await self.users.get_by_id(payload.researcher_id)

        if researcher is None:
            raise NotFoundError("Researcher not found.")

        if researcher.role != UserRole.RESEARCHER:
            raise ConflictError("Only researchers can be added as authors.")

        existing = await self.authors.get_author(
            publication_id,
            payload.researcher_id,
        )

        if existing is not None:
            raise ConflictError("Researcher is already an author of this publication.")

        existing_order = await self.authors.get_by_author_order(
            publication_id,
            payload.author_order,
        )

        if existing_order is not None:
            raise ConflictError("Author order already exists.")

        author = await self.authors.create(
            publication_id=publication.id,
            researcher_id=payload.researcher_id,
            author_order=payload.author_order,
            is_corresponding_author=payload.is_corresponding_author,
        )

        await self.history.log(
            publication_id=publication.id,
            performed_by=current_user.id,
            action=PublicationHistoryAction.AUTHOR_ADDED,
            description=f"Added author '{researcher.full_name}'.",
        )

        await self.session.commit()

        author = await self.authors.get_author(
            publication.id,
            payload.researcher_id,
        )

        return self._to_read_schema(author)

    async def list_authors(
        self,
        publication_id: uuid.UUID,
    ) -> list[PublicationAuthor]:

        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        authors = await self.authors.list_by_publication(publication_id)

        return [self._to_read_schema(author) for author in authors]

    async def remove_author(
        self,
        publication_id: uuid.UUID,
        researcher_id: uuid.UUID,
        current_user: User,
    ) -> None:

        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        if publication.created_by != current_user.id:
            raise ForbiddenError("Only the publication owner can manage authors.")

        author = await self.authors.get_author(
            publication_id,
            researcher_id,
        )

        if author is None:
            raise NotFoundError("Author not found.")

        await self.history.log(
            publication_id=publication.id,
            performed_by=current_user.id,
            action=PublicationHistoryAction.AUTHOR_REMOVED,
            description=f"Removed author '{author.researcher.full_name}'.",
        )

        await self.authors.delete(author)

        await self.session.commit()
