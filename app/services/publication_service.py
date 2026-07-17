import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.schemas.publication import PublicationCreate, PublicationUpdate
from app.schemas.publication_decision import PublicationDecisionCreate, EditorialDecision
from app.services.cloudinary_service import CloudinaryService
from app.models.publication import Publication, PublicationStatus
from app.models.user import User, UserRole
from app.repositories.publication_repository import PublicationRepository
from app.repositories.publication_author_repository import PublicationAuthorRepository
from app.repositories.review_assignment_repository import ReviewAssignmentRepository


class PublicationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.publications = PublicationRepository(session)
        self.author_repository = PublicationAuthorRepository(session)
        self.review_assignments = ReviewAssignmentRepository(session)

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
        )

        await self.session.commit()
        await self.session.refresh(publication)

        return publication

    async def get_publication(self, publication_id: uuid.UUID) -> Publication:
        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        return publication

    async def list_publications(self) -> list[Publication]:
        return await self.publications.list_all()

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

        await self.session.commit()

        await self.session.refresh(publication)

        return publication
