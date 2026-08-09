from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.routes.notifications import create_notification
from app.api.deps import get_current_user
from app.core.audit import log_audit
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReviewerAssignment:
    _require_reviewer_user(db, payload.reviewer_user_id)

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
    log_audit(
        db,
        actor_user_id=current_user.id,
        action="reviewer_assigned",
        entity_type="reviewer_assignment",
        entity_id=assignment.id,
        details=f"reviewer_user_id={payload.reviewer_user_id}",
    )
    scope_label = f"institution #{payload.institution_id}" if payload.institution_id else f"publication #{payload.publication_id}"
    create_notification(
        db,
        recipient_user_id=payload.reviewer_user_id,
        type="reviewer_assigned",
        message=f"You've been assigned to review submissions for {scope_label}",
        link="/publications/review",
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

    log_audit(
        db,
        actor_user_id=current_user.id,
        action="reviewer_unassigned",
        entity_type="reviewer_assignment",
        entity_id=assignment.id,
    )
    db.delete(assignment)
    db.commit()
    