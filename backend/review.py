from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Review, Publication, Researcher, Notification
from schemas import ReviewCreate, ReviewResponse
from auth import get_current_user


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


# =====================================================
# Helper: Get Researcher Linked to Current User
# =====================================================

def get_linked_researcher(
    current_user,
    db: Session
):
    researcher = db.query(Researcher).filter(
        Researcher.user_id == current_user.id
    ).first()

    return researcher


# =====================================================
# Get Reviews
# =====================================================

@router.get(
    "/",
    response_model=list[ReviewResponse]
)
def get_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Researcher is not allowed to access reviews
    if current_user.role == "Researcher":
        raise HTTPException(
            status_code=403,
            detail="Researchers are not allowed to access reviews"
        )

    # Reviewer can see only their assigned reviews
    if current_user.role == "Reviewer":

        researcher = get_linked_researcher(
            current_user,
            db
        )

        if not researcher:
            raise HTTPException(
                status_code=403,
                detail="Reviewer is not linked to a researcher profile"
            )

        return db.query(Review).filter(
            Review.reviewer_id == researcher.researcher_id
        ).all()

    # Institution Admin and System Admin
    # can see all reviews
    if current_user.role in [
        "Institution Admin",
        "System Admin"
    ]:
        return db.query(Review).all()

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to access reviews"
    )


# =====================================================
# Assign Reviewer
# =====================================================

@router.post(
    "/",
    response_model=ReviewResponse
)
def assign_reviewer(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Only Institution Admin and System Admin
    # can assign reviewers
    if current_user.role not in [
        "Institution Admin",
        "System Admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Only Institution Admin or System Admin can assign reviewers"
        )

    # -------------------------------------------------
    # Check publication
    # -------------------------------------------------

    publication = db.query(Publication).filter(
        Publication.publication_id == review.publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    # -------------------------------------------------
    # Check reviewer
    # -------------------------------------------------

    reviewer = db.query(Researcher).filter(
        Researcher.researcher_id == review.reviewer_id
    ).first()

    if not reviewer:
        raise HTTPException(
            status_code=404,
            detail="Reviewer not found"
        )

    # -------------------------------------------------
    # Author cannot review their own publication
    # -------------------------------------------------

    if publication.researcher_id == review.reviewer_id:
        raise HTTPException(
            status_code=400,
            detail="Author cannot review their own publication"
        )

    # -------------------------------------------------
    # Prevent duplicate assignment
    # -------------------------------------------------

    existing_review = db.query(Review).filter(
        Review.publication_id == review.publication_id,
        Review.reviewer_id == review.reviewer_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="Reviewer is already assigned to this publication"
        )

    # -------------------------------------------------
    # Check reviewer has a user account
    # -------------------------------------------------

    if not reviewer.user_id:
        raise HTTPException(
            status_code=400,
            detail="Reviewer is not linked to a user account"
        )

    # -------------------------------------------------
    # Create Review
    # -------------------------------------------------

    new_review = Review(
        publication_id=review.publication_id,
        reviewer_id=review.reviewer_id,
        review_feedback=review.review_feedback,
        decision="Pending",
        status="Pending"
    )

    db.add(new_review)

    # -------------------------------------------------
    # Create Notification
    # -------------------------------------------------

    new_notification = Notification(
        user_id=reviewer.user_id,
        message=(
            f"You have been assigned to review publication: "
            f"{publication.title}"
        ),
        notification_type="Review Assignment",
        is_read=0
    )

    db.add(new_notification)

    # -------------------------------------------------
    # Save Review + Notification
    # -------------------------------------------------

    db.commit()

    db.refresh(new_review)

    return new_review


# =====================================================
# Assigned Reviews
# =====================================================

@router.get(
    "/assigned",
    response_model=list[ReviewResponse]
)
def get_assigned_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Reviewer sees their assigned reviews
    if current_user.role == "Reviewer":

        researcher = get_linked_researcher(
            current_user,
            db
        )

        if not researcher:
            raise HTTPException(
                status_code=403,
                detail="Reviewer is not linked to a researcher profile"
            )

        return db.query(Review).filter(
            Review.reviewer_id == researcher.researcher_id
        ).all()

    # Admins see all reviews
    if current_user.role in [
        "Institution Admin",
        "System Admin"
    ]:
        return db.query(Review).all()

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to access assigned reviews"
    )


# =====================================================
# Pending Reviews
# =====================================================

@router.get(
    "/pending",
    response_model=list[ReviewResponse]
)
def get_pending_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Reviewer sees their pending reviews
    if current_user.role == "Reviewer":

        researcher = get_linked_researcher(
            current_user,
            db
        )

        if not researcher:
            raise HTTPException(
                status_code=403,
                detail="Reviewer is not linked to a researcher profile"
            )

        return db.query(Review).filter(
            Review.reviewer_id == researcher.researcher_id,
            Review.status == "Pending"
        ).all()

    # Admins see all pending reviews
    if current_user.role in [
        "Institution Admin",
        "System Admin"
    ]:
        return db.query(Review).filter(
            Review.status == "Pending"
        ).all()

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to access pending reviews"
    )


# =====================================================
# Completed Reviews
# =====================================================

@router.get(
    "/completed",
    response_model=list[ReviewResponse]
)
def get_completed_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Reviewer sees their completed reviews
    if current_user.role == "Reviewer":

        researcher = get_linked_researcher(
            current_user,
            db
        )

        if not researcher:
            raise HTTPException(
                status_code=403,
                detail="Reviewer is not linked to a researcher profile"
            )

        return db.query(Review).filter(
            Review.reviewer_id == researcher.researcher_id,
            Review.status == "Completed"
        ).all()

    # Admins see all completed reviews
    if current_user.role in [
        "Institution Admin",
        "System Admin"
    ]:
        return db.query(Review).filter(
            Review.status == "Completed"
        ).all()

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to access completed reviews"
    )


# =====================================================
# Submit Review
# =====================================================

@router.put(
    "/{review_id}",
    response_model=ReviewResponse
)
def submit_review(
    review_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Find review
    existing_review = db.query(Review).filter(
        Review.review_id == review_id
    ).first()

    if not existing_review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    # -------------------------------------------------
    # Reviewer can update only their own assigned review
    # -------------------------------------------------

    if current_user.role == "Reviewer":

        researcher = get_linked_researcher(
            current_user,
            db
        )

        if not researcher:
            raise HTTPException(
                status_code=403,
                detail="Reviewer is not linked to a researcher profile"
            )

        if existing_review.reviewer_id != researcher.researcher_id:
            raise HTTPException(
                status_code=403,
                detail="You can submit only your assigned review"
            )

    # -------------------------------------------------
    # Admins can submit/update reviews
    # -------------------------------------------------

    elif current_user.role not in [
        "Institution Admin",
        "System Admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to submit this review"
        )

    # -------------------------------------------------
    # Prevent changing completed review
    # -------------------------------------------------

    if existing_review.status == "Completed":
        raise HTTPException(
            status_code=400,
            detail="This review has already been completed"
        )

    # -------------------------------------------------
    # Update Review
    # -------------------------------------------------

    existing_review.review_feedback = review_data.review_feedback
    existing_review.decision = review_data.decision
    existing_review.status = "Completed"

    db.commit()

    db.refresh(existing_review)

    return existing_review


# =====================================================
# Delete Review
# =====================================================

@router.delete(
    "/{review_id}"
)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Only admins can delete reviews
    if current_user.role not in [
        "Institution Admin",
        "System Admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Only Institution Admin or System Admin can delete reviews"
        )

    # Find review
    existing_review = db.query(Review).filter(
        Review.review_id == review_id
    ).first()

    if not existing_review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    # Delete review
    db.delete(existing_review)

    db.commit()

    return {
        "message": "Review deleted successfully"
    }