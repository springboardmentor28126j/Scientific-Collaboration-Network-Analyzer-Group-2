from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Conference, Publication
from schemas import ConferenceCreate, ConferenceResponse


router = APIRouter(
    prefix="/conferences",
    tags=["Conferences"]
)


# =====================================================
# Get All Conferences
# =====================================================

@router.get("/", response_model=list[ConferenceResponse])
def get_conferences(
    db: Session = Depends(get_db)
):
    return db.query(Conference).all()


# =====================================================
# Get Conference By ID
# =====================================================

@router.get("/{conference_id}", response_model=ConferenceResponse)
def get_conference(
    conference_id: int,
    db: Session = Depends(get_db)
):

    conference = db.query(Conference).filter(
        Conference.conference_id == conference_id
    ).first()

    if not conference:
        raise HTTPException(
            status_code=404,
            detail="Conference not found"
        )

    return conference


# =====================================================
# Create Conference
# =====================================================

@router.post("/", response_model=ConferenceResponse)
def add_conference(
    conference: ConferenceCreate,
    db: Session = Depends(get_db)
):

    # Check whether publication exists
    publication = db.query(Publication).filter(
        Publication.publication_id == conference.publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    new_conference = Conference(
        conference_name=conference.conference_name,
        location=conference.location,
        conference_date=conference.conference_date,
        publication_id=conference.publication_id
    )

    db.add(new_conference)
    db.commit()
    db.refresh(new_conference)

    return new_conference


# =====================================================
# Update Conference
# =====================================================

@router.put("/{conference_id}", response_model=ConferenceResponse)
def update_conference(
    conference_id: int,
    updated_data: ConferenceCreate,
    db: Session = Depends(get_db)
):

    conference = db.query(Conference).filter(
        Conference.conference_id == conference_id
    ).first()

    if not conference:
        raise HTTPException(
            status_code=404,
            detail="Conference not found"
        )

    # Check publication
    publication = db.query(Publication).filter(
        Publication.publication_id == updated_data.publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    conference.conference_name = updated_data.conference_name
    conference.location = updated_data.location
    conference.conference_date = updated_data.conference_date
    conference.publication_id = updated_data.publication_id

    db.commit()
    db.refresh(conference)

    return conference


# =====================================================
# Delete Conference
# =====================================================

@router.delete("/{conference_id}")
def delete_conference(
    conference_id: int,
    db: Session = Depends(get_db)
):

    conference = db.query(Conference).filter(
        Conference.conference_id == conference_id
    ).first()

    if not conference:
        raise HTTPException(
            status_code=404,
            detail="Conference not found"
        )

    db.delete(conference)
    db.commit()

    return {
        "message": "Conference deleted successfully"
    }