from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException
)

from sqlalchemy.orm import Session
from pathlib import Path
import shutil

from app.database.database import SessionLocal
from app.models.conferences import Conference
from app.models.user import User
from app import crud

from app.core.auth import (
    oauth2_scheme,
    decode_access_token
)

router = APIRouter(
    prefix="/conferences",
    tags=["Conferences"]
)

UPLOAD_DIR = "uploads/conferences"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


# -----------------------------
# Database
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Current User
# -----------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(token)

    email = payload.get("sub")

    user = crud.get_user_by_email(
        db,
        email
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


# =====================================================
# GET ALL CONFERENCES
# =====================================================

@router.get("/")
def get_conferences(
    db: Session = Depends(get_db)
):

    return crud.get_all_conferences(db)


# =====================================================
# GET MY CONFERENCES
# =====================================================

@router.get("/my-conferences")
def my_conferences(

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    return crud.get_my_conferences(
        db,
        current_user.id
    )


# =====================================================
# GET SINGLE CONFERENCE
# =====================================================

@router.get("/{conference_id}")
def get_conference(

    conference_id: int,

    db: Session = Depends(get_db)

):

    conference = crud.get_conference_by_id(
        db,
        conference_id
    )

    if not conference:

        raise HTTPException(
            status_code=404,
            detail="Conference not found"
        )

    return conference


# =====================================================
# CREATE CONFERENCE
# =====================================================

@router.post("/")
def create_conference(

    conference_name: str = Form(...),

    organizer: str = Form(...),

    venue: str = Form(...),

    country: str = Form(...),

    conference_date: str = Form(...),

    submission_deadline: str = Form(...),

    registration_deadline: str = Form(...),

    registration_fee: int = Form(...),

    conference_type: str = Form(...),

    website: str = Form(None),

    description: str = Form(None),

    topics: str = Form(None),

    status: str = Form(...),

    banner: UploadFile = File(None),

    brochure: UploadFile = File(None),

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    banner_path = None
    brochure_path = None

    if banner:

        banner_path = f"{UPLOAD_DIR}/{banner.filename}"

        with open(banner_path, "wb") as buffer:

            shutil.copyfileobj(
                banner.file,
                buffer
            )

    if brochure:

        brochure_path = f"{UPLOAD_DIR}/{brochure.filename}"

        with open(brochure_path, "wb") as buffer:

            shutil.copyfileobj(
                brochure.file,
                buffer
            )

    conference = Conference(

        conference_name=conference_name,

        organizer=organizer,

        venue=venue,

        country=country,

        conference_date=conference_date,

        submission_deadline=submission_deadline,

        registration_deadline=registration_deadline,

        registration_fee=registration_fee,

        conference_type=conference_type,

        website=website,

        description=description,

        topics=topics,

        banner_image=banner_path,

        brochure_pdf=brochure_path,

        status=status,

        researcher_id=current_user.id

    )

    return crud.create_conference(
        db,
        conference
    )


# =====================================================
# UPDATE CONFERENCE
# =====================================================

@router.put("/{conference_id}")
def update_conference(
    conference_id: int,
    conference_name: str = Form(...),
    organizer: str = Form(...),
    venue: str = Form(...),
    country: str = Form(...),
    conference_date: str = Form(...),
    submission_deadline: str = Form(...),
    registration_deadline: str = Form(...),
    registration_fee: int = Form(...),
    conference_type: str = Form(...),
    website: str = Form(None),
    description: str = Form(None),
    topics: str = Form(None),
    status: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    conference = crud.get_conference_by_id(db, conference_id)

    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")

    if conference.researcher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    conference.conference_name = conference_name
    conference.organizer = organizer
    conference.venue = venue
    conference.country = country
    conference.conference_date = conference_date
    conference.submission_deadline = submission_deadline
    conference.registration_deadline = registration_deadline
    conference.registration_fee = registration_fee
    conference.conference_type = conference_type
    conference.website = website
    conference.description = description
    conference.topics = topics
    conference.status = status

    db.commit()
    db.refresh(conference)

    return conference


# =====================================================
# DELETE CONFERENCE
# =====================================================

@router.delete("/{conference_id}")
def delete_conference(
    conference_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    conference = crud.get_conference_by_id(db, conference_id)

    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")

    if conference.researcher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    db.delete(conference)
    db.commit()

    return {
        "message": "Conference deleted successfully"
    }