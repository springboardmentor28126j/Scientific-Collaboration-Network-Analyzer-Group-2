import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from app.models.publication import PublicationStatus
from app.models.review_assignment import (
    ReviewAssignment,
    ReviewAssignmentStatus,
)
from app.models.user import User, UserRole
from app.repositories.publication_repository import PublicationRepository
from app.repositories.review_assignment_repository import (
    ReviewAssignmentRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.review_assignment import (
    ReviewAssignmentCreate,
    ReviewAssignmentRead,
)


class ReviewAssignmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.assignments = ReviewAssignmentRepository(session)
        self.publications = PublicationRepository(session)
        self.users = UserRepository(session)

    def _to_read_schema(
        self,
        assignment: ReviewAssignment,
    ) -> ReviewAssignmentRead:
        return ReviewAssignmentRead(
            id=assignment.id,
            publication_id=assignment.publication_id,
            reviewer_id=assignment.reviewer_id,
            reviewer_name=assignment.reviewer.full_name,
            reviewer_email=assignment.reviewer.email,
            assigned_by=assignment.assigned_by,
            status=assignment.status,
            assigned_at=assignment.assigned_at,
            completed_at=assignment.completed_at,
        )

    async def assign_reviewers(
        self,
        publication_id: uuid.UUID,
        payload: ReviewAssignmentCreate,
        current_user: User,
    ) -> list[ReviewAssignmentRead]:

        if current_user.role != UserRole.SUPER_ADMIN:
            raise ForbiddenError("Only the super administrator can assign reviewers.")

        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        if publication.status != PublicationStatus.SUBMITTED:
            raise ConflictError("Only submitted publications can be assigned to reviewers.")

        created_assignments: list[ReviewAssignmentRead] = []

        for reviewer_id in payload.reviewer_ids:
            reviewer = await self.users.get_by_id(reviewer_id)

            if reviewer is None:
                raise NotFoundError(f"Reviewer {reviewer_id} does not exist.")

            if reviewer.role != UserRole.REVIEWER:
                raise ConflictError(f"{reviewer.full_name} is not a reviewer.")

            already_assigned = await self.assignments.already_assigned(
                publication.id,
                reviewer.id,
            )

            if already_assigned:
                raise ConflictError(f"{reviewer.full_name} is already assigned.")

            assignment = await self.assignments.create(
                publication_id=publication.id,
                reviewer_id=reviewer.id,
                assigned_by=current_user.id,
                status=ReviewAssignmentStatus.PENDING,
                assigned_at=datetime.now(UTC),
            )

            assignment = await self.assignments.get_by_id(assignment.id)

            created_assignments.append(self._to_read_schema(assignment))

        publication.status = PublicationStatus.UNDER_REVIEW

        await self.session.commit()

        return created_assignments

    async def list_publication_reviewers(
        self,
        publication_id: uuid.UUID,
    ) -> list[ReviewAssignmentRead]:

        publication = await self.publications.get_by_id(publication_id)

        if publication is None:
            raise NotFoundError("Publication not found.")

        assignments = await self.assignments.list_by_publication(publication_id)

        return [self._to_read_schema(assignment) for assignment in assignments]

    async def list_my_assignments(
        self,
        current_user: User,
    ) -> list[ReviewAssignmentRead]:

        if current_user.role != UserRole.REVIEWER:
            raise ForbiddenError("Only reviewers can access their assignments.")

        assignments = await self.assignments.list_by_reviewer(current_user.id)

        return [self._to_read_schema(assignment) for assignment in assignments]
