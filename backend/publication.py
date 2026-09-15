from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Publication, Researcher, Review
from schemas import (
    PublicationCreate,
    PublicationUpdate,
    PublicationResponse
)
from auth import get_current_user


router = APIRouter(
    prefix="/publications",
    tags=["Publications"]
)


# =====================================================
# Publication Workflow
# =====================================================

ALLOWED_TRANSITIONS = {
    "Draft": ["Submitted"],
    "Submitted": ["Reviewer Assigned"],
    "Reviewer Assigned": ["Review Submitted"],
    "Review Submitted": ["Editorial Decision"],
    "Editorial Decision": ["Published", "Rejected"],
    "Published": ["Archived"],
    "Archived": [],
    "Rejected": []
}


# =====================================================
# Get All Publications
# =====================================================

@router.get("/", response_model=list[PublicationResponse])
def get_publications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # All authenticated roles can view publications
    return db.query(Publication).all()


# =====================================================
# Get Publication By ID
# =====================================================

@router.get("/{publication_id}", response_model=PublicationResponse)
def get_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    publication = db.query(Publication).filter(
        Publication.publication_id == publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    return publication


# =====================================================
# Create Publication
# =====================================================

@router.post("/", response_model=PublicationResponse)
def add_publication(
    publication: PublicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Reviewer cannot create publications
    if current_user.role == "Reviewer":
        raise HTTPException(
            status_code=403,
            detail="Reviewers cannot create publications"
        )

    # Check whether researcher exists
    researcher = db.query(Researcher).filter(
        Researcher.researcher_id == publication.researcher_id
    ).first()

    if not researcher:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    # Researcher can create only their own publication
    if current_user.role == "Researcher":

        if not hasattr(Researcher, "user_id"):
            raise HTTPException(
                status_code=500,
                detail="Researcher user mapping is not configured"
            )

        if researcher.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can create publications only for your own researcher profile"
            )

    # New publications must start as Draft
    initial_status = publication.status or "Draft"

    if initial_status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="New publications must start with Draft status"
        )

    # Create publication
    new_publication = Publication(
        title=publication.title,
        publication_type=publication.publication_type,
        abstract=publication.abstract,
        keywords=publication.keywords,
        author=publication.author,
        journal=publication.journal,
        year=publication.year,
        status="Draft",
        pdf_file=publication.pdf_file,
        researcher_id=publication.researcher_id
    )

    db.add(new_publication)
    db.commit()
    db.refresh(new_publication)

    return new_publication


# =====================================================
# Update Publication
# =====================================================

@router.put("/{publication_id}", response_model=PublicationResponse)
def update_publication(
    publication_id: int,
    updated_data: PublicationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    publication = db.query(Publication).filter(
        Publication.publication_id == publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    # =================================================
    # Reviewer cannot modify publications
    # =================================================

    if current_user.role == "Reviewer":
        raise HTTPException(
            status_code=403,
            detail="Reviewers cannot modify publications"
        )

    # =================================================
    # Researcher ownership validation
    # =================================================

    if current_user.role == "Researcher":

        researcher = db.query(Researcher).filter(
            Researcher.researcher_id == publication.researcher_id
        ).first()

        if not researcher:
            raise HTTPException(
                status_code=404,
                detail="Researcher profile not found"
            )

        if not hasattr(Researcher, "user_id"):
            raise HTTPException(
                status_code=500,
                detail="Researcher user mapping is not configured"
            )

        if researcher.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can modify only your own publications"
            )

        # Researcher can submit their Draft,
        # but cannot directly move it through editorial stages
        if updated_data.status is not None:

            current_status = publication.status
            new_status = updated_data.status

            if current_status == "Draft" and new_status == "Submitted":
                pass
            elif new_status != current_status:
                raise HTTPException(
                    status_code=403,
                    detail="Researchers can only submit their Draft publications"
                )

    # =================================================
    # Update fields
    # =================================================

    update_data = updated_data.model_dump(
        exclude_unset=True
    )

    # =================================================
    # Validate Researcher
    # =================================================

    if updated_data.researcher_id is not None:

        researcher = db.query(Researcher).filter(
            Researcher.researcher_id == updated_data.researcher_id
        ).first()

        if not researcher:
            raise HTTPException(
                status_code=404,
                detail="Researcher not found"
            )

    # =================================================
    # Validate Status Workflow
    # =================================================

    if "status" in update_data:

        new_status = update_data["status"]
        current_status = publication.status

        # Same status is allowed
        if new_status != current_status:

            # Check valid status
            if new_status not in ALLOWED_TRANSITIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid publication status: {new_status}"
                )

            allowed_next_statuses = ALLOWED_TRANSITIONS.get(
                current_status,
                []
            )

            if new_status not in allowed_next_statuses:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Invalid workflow transition: "
                        f"{current_status} → {new_status}"
                    )
                )

            # =========================================
            # Reviewer Assigned Validation
            # =========================================

            if new_status == "Reviewer Assigned":

                review = db.query(Review).filter(
                    Review.publication_id == publication_id
                ).first()

                if not review:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Reviewer must be assigned before "
                            "changing status to Reviewer Assigned"
                        )
                    )

            # =========================================
            # Review Submitted Validation
            # =========================================

            if new_status == "Review Submitted":

                completed_review = db.query(Review).filter(
                    Review.publication_id == publication_id,
                    Review.status == "Completed"
                ).first()

                if not completed_review:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Review must be completed before "
                            "changing status to Review Submitted"
                        )
                    )

            # =========================================
            # Editorial Decision Validation
            # =========================================

            if new_status == "Editorial Decision":

                completed_review = db.query(Review).filter(
                    Review.publication_id == publication_id,
                    Review.status == "Completed"
                ).first()

                if not completed_review:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "A completed review is required "
                            "before editorial decision"
                        )
                    )

            # =========================================
            # Published Validation
            # =========================================

            if new_status == "Published":

                completed_review = db.query(Review).filter(
                    Review.publication_id == publication_id,
                    Review.status == "Completed"
                ).first()

                if not completed_review:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Publication cannot be published "
                            "without a completed review"
                        )
                    )

                if completed_review.decision != "Accepted":
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Publication can be published only "
                            "after an Accepted editorial decision"
                        )
                    )

            # =========================================
            # Archived Validation
            # =========================================

            if new_status == "Archived":

                if publication.status != "Published":
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Only Published publications "
                            "can be archived"
                        )
                    )

    # =================================================
    # Apply Updates
    # =================================================

    for key, value in update_data.items():

        setattr(
            publication,
            key,
            value
        )

    db.commit()
    db.refresh(publication)

    return publication


# =====================================================
# Delete Publication
# =====================================================

@router.delete("/{publication_id}")
def delete_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    publication = db.query(Publication).filter(
        Publication.publication_id == publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    # Reviewer cannot delete
    if current_user.role == "Reviewer":
        raise HTTPException(
            status_code=403,
            detail="Reviewers cannot delete publications"
        )

    # Researcher can delete only their own publication
    if current_user.role == "Researcher":

        researcher = db.query(Researcher).filter(
            Researcher.researcher_id == publication.researcher_id
        ).first()

        if not researcher:
            raise HTTPException(
                status_code=404,
                detail="Researcher profile not found"
            )

        if not hasattr(Researcher, "user_id"):
            raise HTTPException(
                status_code=500,
                detail="Researcher user mapping is not configured"
            )

        if researcher.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can delete only your own publications"
            )

    # Do not delete archived publications
    if publication.status == "Archived":
        raise HTTPException(
            status_code=400,
            detail="Archived publications cannot be deleted"
        )

    db.delete(publication)
    db.commit()

    return {
        "message": "Publication deleted successfully"
    }