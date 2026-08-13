from uuid import UUID

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.institution import Institution
from app.models.publication import Publication, PublicationStatus
from app.models.review_assignment import ReviewAssignment
from app.schemas.dashboard import TopResearcher
from app.schemas.dashboard_filter import DashboardFilter
from app.models.review import Review
from app.models.review_assignment import (
    ReviewAssignment,
    ReviewAssignmentStatus,
)
from app.models.user import User, UserRole
from app.models.publication_author import PublicationAuthor


class DashboardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _publication_query(
        self,
        filters: DashboardFilter,
    ):
        query = select(Publication)

        if filters.institution_id:
            query = query.where(Publication.institution_id == filters.institution_id)

        if filters.researcher_id:
            query = query.where(Publication.created_by == filters.researcher_id)

        return query

    async def total_publications(
        self,
        institution_id: UUID | None = None,
    ) -> int:
        query = select(func.count(Publication.id))

        if institution_id:
            query = query.where(Publication.institution_id == institution_id)

        result = await self.session.execute(query)

        return result.scalar_one()

    async def total_institutions(self) -> int:
        result = await self.session.execute(select(func.count(Institution.id)))
        return result.scalar_one()

    async def total_researchers(
        self,
        institution_id: UUID | None = None,
    ) -> int:

        query = select(func.count(User.id)).where(User.role == UserRole.RESEARCHER)

        if institution_id:
            query = query.where(User.institution_id == institution_id)

        result = await self.session.execute(query)

        return result.scalar_one()

    async def total_reviewers(
        self,
        institution_id: UUID | None = None,
    ) -> int:
        query = select(func.count(User.id)).where(User.role == UserRole.REVIEWER)

        if institution_id:
            query = query.where(User.institution_id == institution_id)

        result = await self.session.execute(query)

        return result.scalar_one()

    async def publication_status_counts(
        self,
        institution_id: UUID | None = None,
    ) -> dict[PublicationStatus, int]:

        query = select(
            Publication.status,
            func.count(Publication.id),
        ).group_by(Publication.status)

        if institution_id:
            query = query.where(Publication.institution_id == institution_id)

        result = await self.session.execute(query)

        rows = result.all()

        counts = {status: 0 for status in PublicationStatus}

        for status, total in rows:
            counts[status] = total

        return counts

    async def researcher_publications(
        self,
        researcher_id: UUID,
    ) -> int:
        result = await self.session.execute(
            select(func.count(Publication.id)).where(Publication.created_by == researcher_id)
        )

        return result.scalar_one()

    async def coauthored_publications(
        self,
        researcher_id: UUID,
    ) -> int:
        result = await self.session.execute(
            select(func.count(PublicationAuthor.publication_id))
            .join(
                Publication,
                Publication.id == PublicationAuthor.publication_id,
            )
            .where(
                PublicationAuthor.researcher_id == researcher_id,
                Publication.created_by != researcher_id,
            )
        )

        return result.scalar_one()

    async def researcher_status_counts(
        self,
        researcher_id: UUID,
    ) -> dict[PublicationStatus, int]:

        query = (
            select(
                Publication.status,
                func.count(func.distinct(Publication.id)),
            )
            .outerjoin(
                PublicationAuthor,
                Publication.id == PublicationAuthor.publication_id,
            )
            .where(
                or_(
                    Publication.created_by == researcher_id,
                    PublicationAuthor.researcher_id == researcher_id,
                )
            )
            .group_by(Publication.status)
        )

        result = await self.session.execute(query)

        rows = result.all()

        counts = {status: 0 for status in PublicationStatus}

        for status, total in rows:
            counts[status] = total

        return counts

    async def assigned_reviews(
        self,
        reviewer_id: UUID,
    ) -> int:
        result = await self.session.execute(
            select(func.count(ReviewAssignment.id)).where(
                ReviewAssignment.reviewer_id == reviewer_id
            )
        )

        return result.scalar_one()

    async def pending_reviews(
        self,
        reviewer_id: UUID,
    ) -> int:
        result = await self.session.execute(
            select(func.count(ReviewAssignment.id)).where(
                ReviewAssignment.reviewer_id == reviewer_id,
                ReviewAssignment.status == ReviewAssignmentStatus.PENDING,
            )
        )

        return result.scalar_one()

    async def completed_reviews(
        self,
        reviewer_id: UUID,
    ) -> int:
        result = await self.session.execute(
            select(func.count(ReviewAssignment.id)).where(
                ReviewAssignment.reviewer_id == reviewer_id,
                ReviewAssignment.status == ReviewAssignmentStatus.COMPLETED,
            )
        )

        return result.scalar_one()

    async def top_researchers(
        self,
        institution_id: UUID | None = None,
        limit: int = 10,
    ) -> list[TopResearcher]:

        query = (
            select(
                User.id,
                User.full_name,
                Institution.name,
                func.count(Publication.id).label("published_papers"),
            )
            .join(
                Publication,
                Publication.created_by == User.id,
            )
            .join(
                Institution,
                Institution.id == User.institution_id,
            )
            .where(
                User.role == UserRole.RESEARCHER,
                Publication.status.in_(
                    [
                        PublicationStatus.PUBLISHED,
                        PublicationStatus.ARCHIVED,
                    ]
                ),
            )
            .group_by(
                User.id,
                User.full_name,
                Institution.name,
            )
            .order_by(
                func.count(Publication.id).desc(),
                User.full_name.asc(),
            )
            .limit(limit)
        )

        if institution_id:
            query = query.where(
                User.institution_id == institution_id,
            )

        result = await self.session.execute(query)

        return [
            TopResearcher(
                id=row.id,
                full_name=row.full_name,
                institution_name=row.name,
                published_papers=row.published_papers,
            )
            for row in result
        ]
