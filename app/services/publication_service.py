import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.schemas.publication import PublicationCreate, PublicationUpdate
from app.schemas.publication_decision import PublicationDecisionCreate, EditorialDecision
from app.schemas.publication import PublicationRead
from app.schemas.publication_filter import PublicationFilter
from app.schemas.publication_catalog import PublicationCatalogItem
from app.schemas.publication_catalog_filter import PublicationCatalogFilter
from app.schemas.pagination import PaginatedResponse
from app.schemas.publication_reference_lookup import PublicationReferenceLookup
from app.schemas.publication_catalog import PublicationCatalogSearchItem, PublicationCatalogItem
from app.services.cloudinary_service import CloudinaryService
from app.services.publication_history_service import PublicationHistoryService
from app.services.notification_service import NotificationService
from app.models.publication import Publication, PublicationStatus
from app.models.publication_history import PublicationHistoryAction
from app.models.user import User, UserRole
from app.repositories.publication_repository import PublicationRepository
from app.repositories.publication_author_repository import PublicationAuthorRepository
from app.repositories.review_assignment_repository import ReviewAssignmentRepository
from app.repositories.user_repository import UserRepository


class PublicationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

        self.publications = PublicationRepository(session)
        self.author_repository = PublicationAuthorRepository(session)
        self.review_assignments = ReviewAssignmentRepository(session)
        self.history = PublicationHistoryService(session)

        self.users = UserRepository(session)
        self.notifications = NotificationService(session)

    async def create_publication(
        self,
        payload: PublicationCreate,
        pdf_file: UploadFile,
        current_user: User,
    ) -> Publication:
        """
        Create a new publication.

        Every newly created publication starts in DRAFT status.
        Only researchers can create publications.
        """

        if current_user.role != UserRole.RESEARCHER:
            raise ForbiddenError("Only researchers can create publications.")

        if payload.doi:
            existing = await self.publications.get_by_doi(payload.doi)
            if existing is not None:
                raise ConflictError("A publication with this DOI already exists.")

        # Upload PDF to Cloudinary
        pdf_url, pdf_public_id = await CloudinaryService.upload_publication_pdf(pdf_file)

        publication = await self.publications.create(
            title=payload.title,
            abstract=payload.abstract,
            publication_type=payload.publication_type,
            doi=payload.doi,
            pdf_url=pdf_url,
            pdf_public_id=pdf_public_id,
            status=PublicationStatus.DRAFT,
            created_by=current_user.id,
            institution_id=current_user.institution_id,
        )

        await self.history.log(
            publication_id=publication.id,
            performed_by=current_user.id,
            action=PublicationHistoryAction.CREATED,
            description="Publication created.",
        )

        await self.session.commit()
        await self.session.refresh(publication)

        return publication

    async def get_publication(self, publication_id: uuid.UUID) -> Publication:
        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        return publication

    async def list_publications(
        self,
        current_user: User,
        filters: PublicationFilter,
    ) -> PaginatedResponse[PublicationRead]:

        items, total = await self.publications.list_publications(
            current_user=current_user,
            filters=filters,
        )

        return PaginatedResponse.create(
            items=items,
            total=total,
            page=filters.page,
            size=filters.size,
        )

    async def update_publication(
        self,
        publication_id: uuid.UUID,
        payload: PublicationUpdate,
        current_user: User,
    ) -> Publication:
        publication = await self.get_publication(publication_id)

        if publication.created_by != current_user.id:
            raise ForbiddenError("You can only update your own publications.")

        if publication.status != PublicationStatus.DRAFT:
            raise ConflictError("Only draft publications can be edited.")

        update_data = payload.model_dump(exclude_unset=True)

        if "doi" in update_data and update_data["doi"]:
            existing = await self.publications.get_by_doi(update_data["doi"])

            if existing is not None and existing.id != publication.id:
                raise ConflictError("A publication with this DOI already exists.")

        publication = await self.publications.update(
            publication,
            **update_data,
        )

        await self.history.log(
            publication_id=publication.id,
            performed_by=current_user.id,
            action=PublicationHistoryAction.UPDATED,
            description="Publication details updated.",
        )

        await self.session.commit()
        await self.session.refresh(publication)

        return publication

    async def delete_publication(
        self,
        publication_id: uuid.UUID,
        current_user: User,
    ) -> None:
        publication = await self.get_publication(publication_id)

        if publication.created_by != current_user.id:
            raise ForbiddenError("You can only delete your own publications.")

        if publication.status != PublicationStatus.DRAFT:
            raise ConflictError("Only draft publications can be deleted.")

        await self.publications.delete(publication)

        await self.session.commit()

    async def submit_publication(
        self,
        publication_id: uuid.UUID,
        current_user: User,
    ) -> Publication:
        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        if publication.created_by != current_user.id:
            raise ForbiddenError("Only the publication owner can submit it.")

        if publication.status != PublicationStatus.DRAFT:
            raise ConflictError("Only draft publications can be submitted.")

        if not publication.pdf_url:
            raise ConflictError("Upload the publication PDF before submitting.")

        authors = await self.author_repository.list_by_publication(publication.id)
        if not authors:
            raise ConflictError("At least one author is required.")

        publication = await self.publications.submit(publication)

        await self.history.log(
            publication_id=publication.id,
            performed_by=current_user.id,
            action=PublicationHistoryAction.SUBMITTED,
            description="Publication submitted for review.",
        )

        await self.session.commit()

        await self.session.refresh(publication)

        return publication

    async def make_editor_decision(
        self,
        publication_id: uuid.UUID,
        payload: PublicationDecisionCreate,
        current_user: User,
    ) -> Publication:
        """
        Make the final editorial decision for a publication.

        Only the SUPER_ADMIN can perform this action.
        """

        # ---------- Permission ----------

        if current_user.role != UserRole.SUPER_ADMIN:
            raise ForbiddenError("Only the super administrator can make editorial decisions.")

        # ---------- Publication ----------

        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        # ---------- Status ----------

        if publication.status != PublicationStatus.UNDER_REVIEW:
            raise ConflictError("Only publications under review can receive an editorial decision.")

        # ---------- Reviews ----------

        completed = await self.review_assignments.all_completed(publication.id)

        if not completed:
            raise ConflictError("All reviewers must submit their reviews before making a decision.")

        # ---------- Decision ----------

        if payload.decision == EditorialDecision.ACCEPTED:
            new_status = PublicationStatus.ACCEPTED

        elif payload.decision == EditorialDecision.REJECTED:
            new_status = PublicationStatus.REJECTED

        else:
            new_status = PublicationStatus.REVISION_REQUIRED

        publication = await self.publications.update_editor_decision(
            publication=publication,
            status=new_status,
            editor_note=payload.editor_note,
            decided_by=current_user.id,
        )

        if payload.decision == EditorialDecision.ACCEPTED:
            action = PublicationHistoryAction.ACCEPTED

        elif payload.decision == EditorialDecision.REJECTED:
            action = PublicationHistoryAction.REJECTED

        else:
            action = PublicationHistoryAction.REVISION_REQUESTED

        await self.history.log(
            publication_id=publication.id,
            performed_by=current_user.id,
            action=action,
            description=payload.editor_note,
        )

        await self.session.commit()

        await self.session.refresh(publication)

        return publication

    async def publish(
        self,
        publication_id: uuid.UUID,
        current_user: User,
    ) -> Publication:

        if current_user.role != UserRole.SUPER_ADMIN:
            raise ForbiddenError("Only the super administrator can publish publications.")

        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        if publication.status == PublicationStatus.PUBLISHED:
            raise ConflictError("Publication is already published.")

        if publication.status != PublicationStatus.ACCEPTED:
            raise ConflictError("Only accepted publications can be published.")

        await self.history.log(
            publication_id=publication.id,
            performed_by=current_user.id,
            action=PublicationHistoryAction.PUBLISHED,
            description="Publication published.",
        )

        publication = await self.publications.publish(publication)

        user_ids = await self.users.get_all_active_user_ids()

        await self.notifications.notify_publication_published(
            user_ids=user_ids,
            publication_id=publication.id,
            publication_title=publication.title,
        )

        await self.session.commit()
        await self.session.refresh(publication)

        return publication

    async def archive(
        self,
        publication_id: uuid.UUID,
        current_user: User,
    ) -> Publication:

        if current_user.role != UserRole.SUPER_ADMIN:
            raise ForbiddenError("Only the super administrator can archive publications.")

        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        if publication.status == PublicationStatus.ARCHIVED:
            raise ConflictError("Publication is already archived.")

        if publication.status != PublicationStatus.PUBLISHED:
            raise ConflictError("Only published publications can be archived.")

        publication = await self.publications.archive(publication)

        await self.history.log(
            publication_id=publication.id,
            performed_by=current_user.id,
            action=PublicationHistoryAction.ARCHIVED,
            description="Publication archived.",
        )

        await self.session.commit()
        await self.session.refresh(publication)

        return publication

    async def download_publication(
        self,
        publication_id: uuid.UUID,
        current_user: User,
    ) -> str:
        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        if not publication.pdf_url:
            raise NotFoundError("Publication PDF not found.")

        if not current_user.is_verified:
            raise ForbiddenError("Only verified users can download publications.")

        return publication.pdf_url

    async def list_catalog(
        self,
        filters: PublicationCatalogFilter,
    ) -> PaginatedResponse[PublicationCatalogItem]:

        publications, total = await self.publications.list_catalog(
            filters=filters,
        )

        return PaginatedResponse.create(
            items=publications,
            page=filters.page,
            size=filters.size,
            total=total,
        )

    async def search_catalog(
        self,
        search: str,
    ) -> list[PublicationCatalogSearchItem]:
        return await self.publications.search_catalog(
            search,
        )

    async def get_catalog_publication(
        self,
        publication_id: uuid.UUID,
    ) -> PublicationReferenceLookup:

        publication = await self.publications.get_catalog_publication(
            publication_id,
        )

        if publication is None:
            raise NotFoundError("Publication not found.")

        ordered_authors = sorted(
            publication.authors,
            key=lambda author: author.author_order,
        )

        authors = [publication.creator.full_name]

        authors.extend(author.researcher.full_name for author in ordered_authors)

        authors = ", ".join(dict.fromkeys(authors))

        publication_name = None

        if publication.conference:
            publication_name = (
                publication.conference.proceedings_name or publication.conference.conference_name
            )

        return PublicationReferenceLookup(
            id=publication.id,
            title=publication.title,
            abstract=publication.abstract,
            authors=authors,
            institution_name=publication.institution.name,
            publication_name=publication_name,
            year=(publication.published_at.year if publication.published_at else None),
            doi=publication.doi,
            url=publication.pdf_url,
            publication_type=publication.publication_type,
        )
