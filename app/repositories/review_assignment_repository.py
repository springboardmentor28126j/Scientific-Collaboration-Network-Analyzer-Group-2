import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.review_assignment import (
    ReviewAssignment,
    ReviewAssignmentStatus,
)
from app.models.user import User


class ReviewAssignmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **fields) -> ReviewAssignment:
        assignment = ReviewAssignment(**fields)
        self.session.add(assignment)
        await self.session.flush()
        return assignment

    async def get_by_id(
        self,
        assignment_id: uuid.UUID,
    ) -> ReviewAssignment | None:
        result = await self.session.execute(
            select(ReviewAssignment)
            .options(selectinload(ReviewAssignment.reviewer))
            .where(ReviewAssignment.id == assignment_id)
        )

        return result.scalar_one_or_none()

    async def list_by_publication(
        self,
        publication_id: uuid.UUID,
    ) -> list[ReviewAssignment]:
        result = await self.session.execute(
            select(ReviewAssignment)
            .options(selectinload(ReviewAssignment.reviewer))
            .where(ReviewAssignment.publication_id == publication_id)
        )

        return list(result.scalars().all())

    async def list_by_reviewer(
        self,
        reviewer_id: uuid.UUID,
    ) -> list[ReviewAssignment]:
        result = await self.session.execute(
            select(ReviewAssignment)
            .options(selectinload(ReviewAssignment.publication))
            .where(ReviewAssignment.reviewer_id == reviewer_id)
        )

        return list(result.scalars().all())

    async def already_assigned(
        self,
        publication_id: uuid.UUID,
        reviewer_id: uuid.UUID,
    ) -> bool:
        result = await self.session.execute(
            select(ReviewAssignment).where(
                ReviewAssignment.publication_id == publication_id,
                ReviewAssignment.reviewer_id == reviewer_id,
            )
        )

        return result.scalar_one_or_none() is not None

    async def mark_completed(
        self,
        assignment: ReviewAssignment,
    ) -> ReviewAssignment:
        assignment.status = ReviewAssignmentStatus.COMPLETED
        assignment.completed_at = datetime.now(UTC)

        await self.session.flush()

        return assignment

    async def all_completed(
        self,
        publication_id: uuid.UUID,
    ) -> bool:

        result = await self.session.execute(
            select(func.count())
            .select_from(ReviewAssignment)
            .where(
                ReviewAssignment.publication_id == publication_id,
                ReviewAssignment.status == ReviewAssignmentStatus.PENDING,
            )
        )

        pending = result.scalar_one()

        return pending == 0
