import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.review import Review
from app.models.review_assignment import ReviewAssignment


class ReviewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **fields) -> Review:
        review = Review(**fields)
        self.session.add(review)
        await self.session.flush()
        return review

    async def get_by_id(
        self,
        review_id: uuid.UUID,
    ) -> Review | None:
        result = await self.session.execute(
            select(Review).options(selectinload(Review.assignment)).where(Review.id == review_id)
        )

        return result.scalar_one_or_none()

    async def get_by_assignment(
        self,
        assignment_id: uuid.UUID,
    ) -> Review | None:
        result = await self.session.execute(
            select(Review).where(Review.assignment_id == assignment_id)
        )

        return result.scalar_one_or_none()

    async def list_by_publication(
        self,
        publication_id: uuid.UUID,
    ) -> list[Review]:
        result = await self.session.execute(
            select(Review)
            .join(ReviewAssignment)
            .options(selectinload(Review.assignment))
            .where(ReviewAssignment.publication_id == publication_id)
        )

        return list(result.scalars().all())
