from datetime import UTC, datetime, timezone
import uuid

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication, PublicationStatus
from app.models.publication_author import PublicationAuthor
from app.models.review_assignment import ReviewAssignment
from app.models.user import User, UserRole

from app.schemas.publication_filter import PublicationFilter


class PublicationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _apply_visibility(
        self,
        query,
        current_user: User,
    ):
        # Super Admin can see everything
        if current_user.role == UserRole.SUPER_ADMIN:
            return query

        # Institution Admin can only see publications from their institution
        if current_user.role == UserRole.INSTITUTION_ADMIN:
            return query.where(Publication.institution_id == current_user.institution_id)

        # Researcher can see publications they created
        # OR publications where they are a co-author
        if current_user.role == UserRole.RESEARCHER:
            return (
                query.outerjoin(
                    PublicationAuthor,
                    Publication.id == PublicationAuthor.publication_id,
                )
                .where(
                    or_(
                        Publication.created_by == current_user.id,
                        PublicationAuthor.researcher_id == current_user.id,
                    )
                )
                .distinct()
            )

        # Reviewer can only see assigned publications
        if current_user.role == UserRole.REVIEWER:
            return (
                query.join(
                    ReviewAssignment,
                    Publication.id == ReviewAssignment.publication_id,
                )
                .where(
                    ReviewAssignment.reviewer_id == current_user.id,
                )
                .distinct()
            )

        return query

    def _apply_search(
        self,
        query,
        filters: PublicationFilter,
    ):
        if not filters.search:
            return query

        search = f"%{filters.search}%"

        return query.where(
            or_(
                Publication.title.ilike(search),
                Publication.abstract.ilike(search),
                Publication.doi.ilike(search),
            )
        )

    def _apply_sort(
        self,
        query,
        filters: PublicationFilter,
    ):
        sort_fields = {
            "created_at": Publication.created_at,
            "title": Publication.title,
            "status": Publication.status,
            "publication_type": Publication.publication_type,
        }

        column = sort_fields.get(
            filters.sort_by,
            Publication.created_at,
        )

        if filters.order == "asc":
            return query.order_by(asc(column))

        return query.order_by(desc(column))

    def _apply_filters(
        self,
        query,
        filters: PublicationFilter,
    ):
        if filters.status:
            query = query.where(Publication.status == filters.status)

        if filters.publication_type:
            query = query.where(Publication.publication_type == filters.publication_type)

        return query

    async def create(self, **fields) -> Publication:
        publication = Publication(**fields)
        self.session.add(publication)
        await self.session.flush()
        return publication

    async def get_by_id(self, publication_id: uuid.UUID) -> Publication | None:
        result = await self.session.execute(
            select(Publication).where(Publication.id == publication_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Publication]:
        result = await self.session.execute(
            select(Publication).order_by(Publication.created_at.desc())
        )
        return list(result.scalars().all())

    async def list(
        self,
        current_user: User,
        filters: PublicationFilter,
    ) -> tuple[list[Publication], int]:
        query = select(Publication).options(
            selectinload(Publication.creator),
            selectinload(Publication.authors),
            selectinload(Publication.review_assignments),
            selectinload(Publication.institution),
        )
        query = self._apply_visibility(query, current_user)

        query = self._apply_search(query, filters)

        query = self._apply_filters(query, filters)

        query = self._apply_sort(query, filters)

        count_query = select(func.count()).select_from(query.order_by(None).subquery())

        total = await self.session.scalar(count_query)

        offset = (filters.page - 1) * filters.size

        query = query.offset(offset).limit(filters.size)

        result = await self.session.execute(query)

        items = result.scalars().unique().all()

        return list(items), total or 0

    async def update(self, publication: Publication, **fields) -> Publication:
        for key, value in fields.items():
            setattr(publication, key, value)

        await self.session.flush()
        return publication

    async def delete(self, publication: Publication) -> None:
        await self.session.delete(publication)
        await self.session.flush()

    async def get_by_doi(self, doi: str) -> Publication | None:
        result = await self.session.execute(select(Publication).where(Publication.doi == doi))
        return result.scalar_one_or_none()

    async def submit(self, publication: Publication) -> Publication:
        publication.status = PublicationStatus.SUBMITTED
        publication.submitted_at = datetime.now(UTC)

        await self.session.flush()
        return publication

    async def update_editor_decision(
        self,
        publication: Publication,
        status: PublicationStatus,
        editor_note: str,
        decided_by: uuid.UUID,
    ) -> Publication:

        publication.status = status
        publication.editor_note = editor_note
        publication.decided_by = decided_by
        publication.decision_at = datetime.now(UTC)

        await self.session.flush()

        return publication

    async def publish(
        self,
        publication: Publication,
    ) -> Publication:
        publication.status = PublicationStatus.PUBLISHED
        publication.published_at = datetime.now(timezone.utc)

        await self.session.flush()

        return publication

    async def archive(
        self,
        publication: Publication,
    ) -> Publication:
        publication.status = PublicationStatus.ARCHIVED
        publication.archived_at = datetime.now(timezone.utc)

        await self.session.flush()

        return publication
