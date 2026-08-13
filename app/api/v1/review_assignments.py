import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import get_review_assignment_service
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.review_assignment import (
    ReviewAssignmentCreate,
    ReviewAssignmentRead,
)
from app.services.review_assignment_service import ReviewAssignmentService

router = APIRouter(
    prefix="/review-assignments",
    tags=["Review Assignments"],
)


@router.post(
    "/publications/{publication_id}",
    response_model=list[ReviewAssignmentRead],
    status_code=status.HTTP_201_CREATED,
    summary="Assign reviewers to a publication",
    description=(
        "Super admin only. Assign one or more reviewers to a submitted "
        "publication. Once reviewers are assigned, the publication "
        "automatically moves to UNDER_REVIEW."
    ),
)
async def assign_reviewers(
    publication_id: uuid.UUID,
    payload: ReviewAssignmentCreate,
    current_user: User = Depends(get_current_user),
    review_assignment_service: ReviewAssignmentService = Depends(
        get_review_assignment_service,
    ),
):
    return await review_assignment_service.assign_reviewers(
        publication_id=publication_id,
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/publication/{publication_id}",
    response_model=list[ReviewAssignmentRead],
    summary="List reviewers assigned to a publication",
)
async def list_publication_reviewers(
    publication_id: uuid.UUID,
    review_assignment_service: ReviewAssignmentService = Depends(
        get_review_assignment_service,
    ),
):
    return await review_assignment_service.list_publication_reviewers(
        publication_id,
    )


@router.get(
    "/my",
    response_model=list[ReviewAssignmentRead],
    summary="List my assigned publications",
    description=(
        "Reviewer only. Returns all publications currently assigned to the authenticated reviewer."
    ),
)
async def list_my_assignments(
    current_user: User = Depends(get_current_user),
    review_assignment_service: ReviewAssignmentService = Depends(
        get_review_assignment_service,
    ),
):
    return await review_assignment_service.list_my_assignments(
        current_user,
    )
