from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud import create_notification
from app import schemas, models
from app.models import User
from app.database import SessionLocal
from app.oauth2 import get_current_user


router = APIRouter(
    prefix="/reviewer",
    tags=["Reviewer"]
)


# ==========================
# Database Dependency
# ==========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# ==========================
# Assign Publication
# System Admin Only
# ==========================

@router.post("/assign", response_model=schemas.ReviewResponse)
def assign_publication(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Only System Admin can assign reviewers
    if current_user.role != "system_admin":
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can assign publications to reviewers."
        )

    # Check publication
    publication = db.query(models.Publication).filter(
        models.Publication.id == review.publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found."
        )

    # Only Submitted publications can be assigned
    if publication.status != "Submitted":
        raise HTTPException(
            status_code=400,
            detail="Only submitted publications can be assigned for review."
        )

    # Check reviewer
    reviewer = db.query(User).filter(
        User.id == review.reviewer_id,
        User.role == "reviewer"
    ).first()

    if not reviewer:
        raise HTTPException(
            status_code=404,
            detail="Reviewer not found."
        )

    # -----------------------------------------
    # Check whether publication is already assigned
    # -----------------------------------------

    existing_review = db.query(models.Review).filter(
        models.Review.publication_id == review.publication_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="This publication has already been assigned to a reviewer."
        )

    # -----------------------------------------
    # Create review assignment
    # -----------------------------------------

    db_review = models.Review(
        publication_id=review.publication_id,
        reviewer_id=review.reviewer_id,
        decision="Pending"
    )

    db.add(db_review)

    try:
        db.commit()
        db.refresh(db_review)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to assign publication to reviewer."
        )

    # =====================================
    # REVIEW ASSIGNMENT NOTIFICATION
    # =====================================

    create_notification(
        db,
        schemas.NotificationCreate(
            receiver_id=reviewer.id,
            sender_id=current_user.id,
            title="Publication Assigned for Review",
            message=f'You have been assigned to review the publication "{publication.title}".',
            notification_type="review",
            reference_id=db_review.id,
            reference_type="review"
        )
    )

    return db_review

# ==========================
# Reviewer - My Assignments
# ==========================

@router.get(
    "/my-reviews",
    response_model=list[schemas.ReviewResponse]
)
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Only Reviewer can access this
    if current_user.role != "reviewer":
        raise HTTPException(
            status_code=403,
            detail="Only reviewers can access assigned reviews."
        )

    reviews = db.query(models.Review).filter(
        models.Review.reviewer_id == current_user.id
    ).all()

    return reviews


# ==========================
# Reviewer - Submit Review
# ==========================

@router.put(
    "/reviews/{review_id}",
    response_model=schemas.ReviewResponse
)
def submit_review(
    review_id: int,
    review: schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Only Reviewer can submit reviews
    if current_user.role != "reviewer":
        raise HTTPException(
            status_code=403,
            detail="Only reviewers can submit reviews."
        )

    # Find review
    db_review = db.query(models.Review).filter(
        models.Review.id == review_id
    ).first()

    if not db_review:
        raise HTTPException(
            status_code=404,
            detail="Review assignment not found."
        )

    # Security check
    if db_review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to review this publication."
        )

    # Validate decision
    allowed_decisions = [
        "Pending",
        "Approved",
        "Rejected",
        "Needs Revision"
    ]

    if review.decision not in allowed_decisions:
        raise HTTPException(
            status_code=400,
            detail="Invalid review decision."
        )

    # Update review
    db_review.decision = review.decision
    db_review.comments = review.comments

    # Get publication
    publication = db.query(models.Publication).filter(
        models.Publication.id == db_review.publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found."
        )

    # Update publication status
    if review.decision == "Approved":
        publication.status = "Published"

    elif review.decision == "Rejected":
        publication.status = "Rejected"

    elif review.decision == "Needs Revision":
        publication.status = "Under Review"

    db.commit()
    db.refresh(db_review)

    # =====================================
    # REVIEW NOTIFICATIONS
    # =====================================

    # Get Publication Owner
    publication_owner = db.query(models.Researcher).filter(
        models.Researcher.id == publication.researcher_id
    ).first()

    if publication_owner:

        # ---------------------------------
        # 1. Researcher Notification
        # ---------------------------------

        create_notification(
            db,
            schemas.NotificationCreate(
                receiver_id=publication_owner.user_id,
                sender_id=current_user.id,
                title="Publication Review Completed",
                message=f'Your publication "{publication.title}" has been {review.decision.lower()}.',
                notification_type="review",
                reference_id=db_review.id,
                reference_type="review"
            )
        )

        # ---------------------------------
        # 2. Institution Admin Notification
        # ---------------------------------

        institution = db.query(models.Institution).filter(
            models.Institution.name == publication_owner.institution
        ).first()

        if institution:

            create_notification(
                db,
                schemas.NotificationCreate(
                    receiver_id=institution.user_id,
                    sender_id=current_user.id,
                    title="Publication Review Completed",
                    message=f'The publication "{publication.title}" by {publication_owner.full_name} has been {review.decision.lower()}.',
                    notification_type="review",
                    reference_id=db_review.id,
                    reference_type="review"
                )
            )

    # ---------------------------------
    # 3. System Admin Notification
    # ---------------------------------

    system_admins = db.query(models.User).filter(
        models.User.role == "system_admin"
    ).all()

    for admin in system_admins:

        create_notification(
            db,
            schemas.NotificationCreate(
                receiver_id=admin.id,
                sender_id=current_user.id,
                title="Publication Review Completed",
                message=f'The publication "{publication.title}" has been {review.decision.lower()} by a reviewer.',
                notification_type="review",
                reference_id=db_review.id,
                reference_type="review"
            )
        )

    return db_review

@router.get(
    "/all-reviews",
    response_model=list[schemas.ReviewResponse]
)
def get_all_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "system_admin":
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can access all reviews."
        )

    reviews = db.query(models.Review).all()

    return reviews