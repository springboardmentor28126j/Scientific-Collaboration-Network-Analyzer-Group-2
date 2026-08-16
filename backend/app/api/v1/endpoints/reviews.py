from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.conference import Conference, ConferenceParticipation, SubmissionStatus
from app.models.publication import Publication, PublicationStatus
from app.models.researcher import ResearcherProfile
from app.models.review import Review, ReviewTargetType, ReviewStatus
from app.models.user import User, UserRole
from app.repositories import user_repository
from app.schemas.review import ReviewAssign, ReviewSubmit, ReviewOut
from app.utils.audit import write_audit_log
from app.utils.notifications import notify

router = APIRouter(prefix="/reviews", tags=["Reviews"])


def _get_target(db: Session, target_type: ReviewTargetType, target_id: int):
    if target_type == ReviewTargetType.PUBLICATION:
        return db.get(Publication, target_id)
    return db.get(ConferenceParticipation, target_id)


def _target_owner_user_id(db: Session, target_type: ReviewTargetType, target) -> int | None:
    researcher_id = target.primary_author_id if target_type == ReviewTargetType.PUBLICATION else target.researcher_id
    profile = db.get(ResearcherProfile, researcher_id)
    return profile.user_id if profile else None


def _target_link_url(target_type: ReviewTargetType, target) -> str:
    if target_type == ReviewTargetType.PUBLICATION:
        return f"/publications/{target.publication_id}"
    return f"/conferences/{target.conference_id}"


def _target_label(target_type: ReviewTargetType) -> str:
    return "publication" if target_type == ReviewTargetType.PUBLICATION else "conference submission"


def _target_institution_id(db: Session, target_type: ReviewTargetType, target) -> int | None:
    if target_type == ReviewTargetType.PUBLICATION:
        return target.institution_id
    conference = db.get(Conference, target.conference_id)
    return conference.organizing_institution_id if conference else None


def _require_can_assign(current_user: User, target_institution_id: int | None) -> None:
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return
    if current_user.role == UserRole.INSTITUTION_ADMIN and target_institution_id == current_user.institution_id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only the relevant institution admin (or a system admin) can assign reviewers",
    )


def _should_reveal_reviewer_identity(db: Session, current_user: User, review: Review) -> bool:
    """
    Blind peer review: the person whose work is being reviewed (and any
    other reviewer on the same item) shouldn't see who the reviewer is --
    only that a review exists, with its score/comments/recommendation.
    Reviewer identity stays visible to: the reviewer themselves, whoever
    assigned the review, the relevant institution admin, and system admin --
    all of whom need it to actually manage the review process.
    """
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return True
    if current_user.user_id in (review.reviewer_id, review.assigned_by):
        return True
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        target = _get_target(db, review.target_type, review.target_id)
        if target is not None and _target_institution_id(db, review.target_type, target) == current_user.institution_id:
            return True
    return False


def _serialize_review(db: Session, current_user: User, review: Review) -> ReviewOut:
    out = ReviewOut.model_validate(review)
    if not _should_reveal_reviewer_identity(db, current_user, review):
        out.reviewer_id = None
    return out


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def assign_review(
    payload: ReviewAssign,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    target = _get_target(db, payload.target_type, payload.target_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{payload.target_type.value} not found")

    _require_can_assign(current_user, _target_institution_id(db, payload.target_type, target))

    reviewer = user_repository.get_by_id(db, payload.reviewer_id)
    if reviewer is None or reviewer.role != UserRole.REVIEWER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reviewer_id must belong to a Reviewer account")
    if current_user.role == UserRole.INSTITUTION_ADMIN and reviewer.institution_id != current_user.institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only assign reviewers from your own institution",
        )

    existing = db.scalar(
        select(Review).where(
            Review.target_type == payload.target_type,
            Review.target_id == payload.target_id,
            Review.reviewer_id == payload.reviewer_id,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This reviewer is already assigned to this item")

    review = Review(
        target_type=payload.target_type, target_id=payload.target_id,
        reviewer_id=payload.reviewer_id, assigned_by=current_user.user_id,
    )
    db.add(review)

    # BR flow: "Submitted -> Reviewer Assigned -> Review -> ... -> Accepted".
    # Assigning the first reviewer is what actually moves something out of
    # the submitted queue and into review.
    if payload.target_type == ReviewTargetType.PUBLICATION and target.status == PublicationStatus.SUBMITTED:
        target.status = PublicationStatus.UNDER_REVIEW
    elif payload.target_type == ReviewTargetType.CONFERENCE_SUBMISSION and target.submission_status == SubmissionStatus.SUBMITTED:
        target.submission_status = SubmissionStatus.UNDER_REVIEW

    db.commit()
    db.refresh(review)
    write_audit_log(db, current_user.user_id, "CREATE", "review", review.review_id)
    notify(
        db, reviewer.user_id, "review_assigned", "New review assignment",
        f"You've been asked to review a {_target_label(payload.target_type)}.",
        link_url=f"/reviewer/reviews/{review.review_id}",
    )
    return review


@router.get("/mine", response_model=list[ReviewOut])
def list_my_reviews(
    status_filter: ReviewStatus | None = Query(None, alias="status"),
    target_type: ReviewTargetType | None = Query(None),
    current_user: User = Depends(require_roles(UserRole.REVIEWER)),
    db: Session = Depends(get_db),
):
    stmt = select(Review).where(Review.reviewer_id == current_user.user_id)
    if status_filter is not None:
        stmt = stmt.where(Review.status == status_filter)
    if target_type is not None:
        stmt = stmt.where(Review.target_type == target_type)
    stmt = stmt.order_by(Review.assigned_at.desc())
    return list(db.scalars(stmt).all())


def _require_target_visibility(db: Session, current_user: User, review: Review) -> None:
    """Who can see a given review: the reviewer themselves, whoever assigned
    it, the relevant institution admin, system admin, or the person who owns
    the thing being reviewed (they can see review outcomes, just not edit them)."""
    if current_user.role == UserRole.SYSTEM_ADMIN or current_user.user_id in (review.reviewer_id, review.assigned_by):
        return
    target = _get_target(db, review.target_type, review.target_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review target no longer exists")

    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if _target_institution_id(db, review.target_type, target) == current_user.institution_id:
            return

    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    if profile is not None:
        owner_researcher_id = (
            target.primary_author_id if review.target_type == ReviewTargetType.PUBLICATION else target.researcher_id
        )
        if owner_researcher_id == profile.researcher_id:
            return

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot view this review")


@router.get("/{review_id}", response_model=ReviewOut)
def get_review(review_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    _require_target_visibility(db, current_user, review)
    return _serialize_review(db, current_user, review)


@router.get("", response_model=list[ReviewOut])
def list_reviews_for_target(
    target_type: ReviewTargetType = Query(...),
    target_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target = _get_target(db, target_type, target_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{target_type.value} not found")

    if current_user.role != UserRole.SYSTEM_ADMIN:
        allowed = False
        if current_user.role == UserRole.INSTITUTION_ADMIN:
            allowed = _target_institution_id(db, target_type, target) == current_user.institution_id
        if not allowed:
            profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
            if profile is not None:
                owner_researcher_id = (
                    target.primary_author_id if target_type == ReviewTargetType.PUBLICATION else target.researcher_id
                )
                allowed = owner_researcher_id == profile.researcher_id
        if not allowed:
            # A reviewer can also see the roster of reviews for something they're personally reviewing.
            allowed = db.scalar(
                select(Review).where(
                    Review.target_type == target_type, Review.target_id == target_id,
                    Review.reviewer_id == current_user.user_id,
                )
            ) is not None
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot view reviews for this item")

    stmt = select(Review).where(Review.target_type == target_type, Review.target_id == target_id)
    reviews = list(db.scalars(stmt).all())
    return [_serialize_review(db, current_user, r) for r in reviews]


def _require_own_review(current_user: User, review: Review) -> None:
    if current_user.role != UserRole.REVIEWER or review.reviewer_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This isn't your review to act on")


@router.post("/{review_id}/accept", response_model=ReviewOut)
def accept_review(review_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    _require_own_review(current_user, review)
    if review.status != ReviewStatus.ASSIGNED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This review invitation has already been responded to")

    review.status = ReviewStatus.ACCEPTED
    review.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(review)
    write_audit_log(db, current_user.user_id, "UPDATE", "review", review.review_id, details="Accepted")
    target = _get_target(db, review.target_type, review.target_id)
    if target is not None:
        notify(
            db, review.assigned_by, "review_accepted", "Review invitation accepted",
            f"A reviewer accepted the {_target_label(review.target_type)} review you assigned.",
            link_url=_target_link_url(review.target_type, target),
        )
    return review


@router.post("/{review_id}/decline", response_model=ReviewOut)
def decline_review(review_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    _require_own_review(current_user, review)
    if review.status != ReviewStatus.ASSIGNED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This review invitation has already been responded to")

    review.status = ReviewStatus.DECLINED
    review.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(review)
    write_audit_log(db, current_user.user_id, "UPDATE", "review", review.review_id, details="Declined")
    target = _get_target(db, review.target_type, review.target_id)
    if target is not None:
        notify(
            db, review.assigned_by, "review_declined", "Review invitation declined",
            f"A reviewer declined the {_target_label(review.target_type)} review you assigned. You may want to assign someone else.",
            link_url=_target_link_url(review.target_type, target),
        )
    return review


@router.patch("/{review_id}/submit", response_model=ReviewOut)
def submit_review(
    review_id: int, payload: ReviewSubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    _require_own_review(current_user, review)
    if review.status != ReviewStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must accept the review invitation before submitting your evaluation",
        )

    review.score = payload.score
    review.comments = payload.comments
    review.recommendation = payload.recommendation
    review.status = ReviewStatus.COMPLETED
    review.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(review)
    write_audit_log(
        db, current_user.user_id, "UPDATE", "review", review.review_id,
        details=f"Completed with recommendation={payload.recommendation.value}",
    )

    target = _get_target(db, review.target_type, review.target_id)
    if target is not None:
        link_url = _target_link_url(review.target_type, target)
        label = _target_label(review.target_type)
        recommendation_text = payload.recommendation.value.replace("_", " ")
        owner_user_id = _target_owner_user_id(db, review.target_type, target)
        notify(
            db, owner_user_id, "review_completed", "A review of your submission is complete",
            f"Your {label} was reviewed with a recommendation of: {recommendation_text}.",
            link_url=link_url,
        )
        if review.assigned_by != owner_user_id:
            notify(
                db, review.assigned_by, "review_completed", "Review completed",
                f"The {label} review you assigned is complete. Recommendation: {recommendation_text}.",
                link_url=link_url,
            )
    return review
