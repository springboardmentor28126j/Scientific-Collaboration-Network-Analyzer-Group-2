from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Review, Publication, Researcher
from schemas import ReviewCreate, ReviewResponse


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


# =====================================================
# Get All Reviews
# =====================================================

@router.get("/", response_model=list[ReviewResponse])
def get_reviews(db: Session = Depends(get_db)):

    return db.query(Review).all()


# =====================================================
# Assign Reviewer
# =====================================================

@router.post("/", response_model=ReviewResponse)
def assign_reviewer(
    review: ReviewCreate,
    db: Session = Depends(get_db)
):

    # Check publication
    publication = db.query(Publication).filter(
        Publication.publication_id == review.publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    # Check reviewer
    reviewer = db.query(Researcher).filter(
        Researcher.researcher_id == review.reviewer_id
    ).first()

    if not reviewer:
        raise HTTPException(
            status_code=404,
            detail="Reviewer not found"
        )

    # Author cannot review own publication
    if publication.researcher_id == review.reviewer_id:
        raise HTTPException(
            status_code=400,
            detail="Author cannot review their own publication"
        )

    # Prevent duplicate review
    existing_review = db.query(Review).filter(
        Review.publication_id == review.publication_id,
        Review.reviewer_id == review.reviewer_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="Reviewer is already assigned to this publication"
        )

    # Create review
    new_review = Review(
        publication_id=review.publication_id,
        reviewer_id=review.reviewer_id,
        review_feedback=review.review_feedback,
        decision=review.decision,
        status=review.status
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review
# =====================================================
# Assigned Reviews
# =====================================================

@router.get("/assigned", response_model=list[ReviewResponse])
def get_assigned_reviews(db: Session = Depends(get_db)):

    return db.query(Review).all()


# =====================================================
# Pending Reviews
# =====================================================

@router.get("/pending", response_model=list[ReviewResponse])
def get_pending_reviews(db: Session = Depends(get_db)):

    return db.query(Review).filter(
        Review.status == "Pending"
    ).all()


# =====================================================
# Completed Reviews
# =====================================================

@router.get("/completed", response_model=list[ReviewResponse])
def get_completed_reviews(db: Session = Depends(get_db)):

    return db.query(Review).filter(
        Review.status == "Completed"
    ).all()

# =====================================================
# Submit Review Feedback
# =====================================================

@router.put("/{review_id}", response_model=ReviewResponse)
def submit_review(
    review_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db)
):

    existing_review = db.query(Review).filter(
        Review.review_id == review_id
    ).first()

    if not existing_review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    existing_review.review_feedback = review_data.review_feedback
    existing_review.decision = review_data.decision
    existing_review.status = "Completed"

    db.commit()
    db.refresh(existing_review)

    return existing_review


# =====================================================
# Delete Review
# =====================================================

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db)
):

    existing_review = db.query(Review).filter(
        Review.review_id == review_id
    ).first()

    if not existing_review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    db.delete(existing_review)
    db.commit()

    return {
        "message": "Review deleted successfully"
    }