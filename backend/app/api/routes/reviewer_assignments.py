from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.email import send_email
from app.core.notifications import create_notification
from app.db.session import get_db
from app.models.institution import Institution
from app.models.publication import Publication
from app.models.reviewer_assignment import ReviewerAssignment
from app.models.user import User, UserRole
from app.schemas.reviewer_assignment import ReviewerAssignmentCreate, ReviewerAssignmentOut

router = APIRouter()


def _require_reviewer_user(db: Session, reviewer_user_id: int) -> User:
    reviewer = db.query(User).filter(User.id == reviewer_user_id).first()
    if reviewer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reviewer user not found"
        )
    if reviewer.role != UserRole.REVIEWER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That user does not have the Reviewer role",
        )
    return reviewer


@router.post("", response_model=ReviewerAssignmentOut, status_code=status.HTTP_201_CREATED)
def create_reviewer_assignment(
    payload: ReviewerAssignmentCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReviewerAssignment:
    reviewer = _require_reviewer_user(db, payload.reviewer_user_id)

    if payload.publication_id is not None:
        # Per-publication assignment is a System Admin power only.
        if current_user.role != UserRole.SYSTEM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only a System Admin can assign a reviewer to a specific publication",
            )
        publication = (
            db.query(Publication).filter(Publication.id == payload.publication_id).first()
        )
        if publication is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found"
            )

    if payload.institution_id is not None:
        institution = (
            db.query(Institution).filter(Institution.id == payload.institution_id).first()
        )
        if institution is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
            )
        # System Admin can assign for any institution; an Institution Admin
        # only for the institution they administer.
        if (
            current_user.role != UserRole.SYSTEM_ADMIN
            and institution.admin_user_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only assign reviewers for an institution you administer",
            )

    assignment = ReviewerAssignment(
        reviewer_user_id=payload.reviewer_user_id,
        institution_id=payload.institution_id,
        publication_id=payload.publication_id,
        assigned_by=current_user.id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    scope_desc = (
        "a specific publication" if payload.publication_id is not None else "an institution"
    )
    create_notification(
        db,
        user_id=reviewer.id,
        type="reviewer_assignment_created",
        message=f"You were assigned as a reviewer for {scope_desc}",
        link_url=None,
    )
    background_tasks.add_task(
        send_email,
        reviewer.email,
        "New reviewer assignment",
        f"You were assigned as a reviewer for {scope_desc}. Log in to SCNA to see the review queue.",
    )

    return assignment


@router.get("", response_model=list[ReviewerAssignmentOut])
def list_reviewer_assignments(
    institution_id: int | None = None,
    reviewer_user_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReviewerAssignment]:
    query = db.query(ReviewerAssignment)
    if institution_id is not None:
        query = query.filter(ReviewerAssignment.institution_id == institution_id)
    if reviewer_user_id is not None:
        query = query.filter(ReviewerAssignment.reviewer_user_id == reviewer_user_id)
    return query.order_by(ReviewerAssignment.id.desc()).all()


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reviewer_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    assignment = (
        db.query(ReviewerAssignment).filter(ReviewerAssignment.id == assignment_id).first()
    )
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
        )

    if current_user.role != UserRole.SYSTEM_ADMIN:
        if assignment.publication_id is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only a System Admin can remove a publication-level assignment",
            )
        institution = (
            db.query(Institution).filter(Institution.id == assignment.institution_id).first()
        )
        if institution is None or institution.admin_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage reviewers for an institution you administer",
            )

    db.delete(assignment)
    db.commit()
