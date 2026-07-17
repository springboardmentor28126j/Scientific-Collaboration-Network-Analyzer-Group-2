import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from app.models.publication_history import PublicationHistoryAction
from app.models.review import Review
from app.models.review_assignment import ReviewAssignmentStatus
from app.models.user import User, UserRole
from app.repositories.review_assignment_repository import (
    ReviewAssignmentRepository,
)
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import ReviewCreate, ReviewRead
from app.services.publication_history_service import PublicationHistoryService


class ReviewService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.reviews = ReviewRepository(session)
        self.assignments = ReviewAssignmentRepository(session)
        self.history = PublicationHistoryService(session)

    def _to_read_schema(
        self,
        review: Review,
    ) -> ReviewRead:
        return ReviewRead(
            id=review.id,
            assignment_id=review.assignment_id,
            decision=review.decision,
            score=review.score,
            strengths=review.strengths,
            weaknesses=review.weaknesses,
            comments=review.comments,
            recommendation=review.recommendation,
            submitted_at=review.submitted_at,
        )

    async def submit_review(
        self,
        payload: ReviewCreate,
        current_user: User,
    ) -> ReviewRead:

        if current_user.role != UserRole.REVIEWER:
            raise ForbiddenError("Only reviewers can submit reviews.")

        assignment = await self.assignments.get_by_id(payload.assignment_id)

        if assignment is None:
            raise NotFoundError("Review assignment not found.")

        if assignment.reviewer_id != current_user.id:
            raise ForbiddenError("This assignment does not belong to you.")

        if assignment.status != ReviewAssignmentStatus.PENDING:
            raise ConflictError("This review assignment has already been completed.")

        existing_review = await self.reviews.get_by_assignment(assignment.id)

        if existing_review is not None:
            raise ConflictError("You have already submitted a review.")

        review = await self.reviews.create(
            assignment_id=assignment.id,
            decision=payload.decision,
            score=payload.score,
            strengths=payload.strengths,
            weaknesses=payload.weaknesses,
            comments=payload.comments,
            recommendation=payload.recommendation,
            submitted_at=datetime.now(UTC),
        )

        await self.assignments.mark_completed(assignment)

        await self.history.log(
            publication_id=assignment.publication_id,
            performed_by=current_user.id,
            action=PublicationHistoryAction.REVIEW_SUBMITTED,
            description="Review submitted.",
        )

        await self.session.commit()

        review = await self.reviews.get_by_id(review.id)

        return self._to_read_schema(review)

    async def get_review(
        self,
        review_id: uuid.UUID,
    ) -> ReviewRead:

        review = await self.reviews.get_by_id(review_id)

        if review is None:
            raise NotFoundError("Review not found.")

        return self._to_read_schema(review)

    async def list_publication_reviews(
        self,
        publication_id: uuid.UUID,
    ) -> list[ReviewRead]:

        reviews = await self.reviews.list_by_publication(publication_id)

        return [self._to_read_schema(review) for review in reviews]
