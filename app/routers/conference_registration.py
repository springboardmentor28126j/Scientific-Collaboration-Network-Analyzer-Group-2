from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app import schemas, crud, models
from app.oauth2 import get_current_user
from app.models import User


router = APIRouter(
    prefix="/conference-registration",
    tags=["Conference Registration"]
)



def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



# ---------------- Register Conference ----------------


# ---------------- Register Conference ----------------


@router.post(
    "/",
    response_model=schemas.ConferenceRegistrationResponse
)
def register_conference(

    registration: schemas.ConferenceRegistrationCreate,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):


    # Get researcher profile of logged-in user

    researcher = db.query(
        models.Researcher
    ).filter(
        models.Researcher.user_id == current_user.id
    ).first()


    if not researcher:

        raise HTTPException(
            status_code=404,
            detail="Researcher profile not found"
        )



    # ==============================
    # Get Conference
    # ==============================

    conference = db.query(
        models.Conference
    ).filter(
        models.Conference.id == registration.conference_id
    ).first()



    if not conference:

        raise HTTPException(
            status_code=404,
            detail="Conference not found"
        )



    # ==============================
    # Conference Date Validation
    # ==============================

    conference_date = datetime.strptime(
        conference.conference_date,
        "%Y-%m-%d"
    )


    if datetime.now().date() >= conference_date.date():

        raise HTTPException(
            status_code=400,
            detail="Registration closed. Conference date has passed."
        )



    # ==============================
    # Duplicate Registration Check
    # ==============================

    existing_registration = db.query(
        models.ConferenceRegistration
    ).filter(
        models.ConferenceRegistration.researcher_id == researcher.id,
        models.ConferenceRegistration.conference_id == registration.conference_id
    ).first()



    if existing_registration:

        raise HTTPException(
            status_code=400,
            detail="You have already registered for this conference"
        )



    # ==============================
    # Presenter Validation
    # ==============================

    if registration.participation_type == "Presenter":


        if not registration.publication_id:

            raise HTTPException(
                status_code=400,
                detail="Presenter must select publication"
            )


        if not registration.presentation_title:

            raise HTTPException(
                status_code=400,
                detail="Presentation title is required"
            )


        if not registration.presentation_mode:

            raise HTTPException(
                status_code=400,
                detail="Presentation mode is required"
            )



    # ==============================
    # Attendee Validation
    # ==============================

    if registration.participation_type == "Attendee":

        registration.publication_id = None
        registration.presentation_title = None
        registration.presentation_mode = None



    # ==============================
    # Save Registration
    # ==============================

    return crud.create_conference_registration(

        db,

        registration,

        researcher.id

    )

# ---------------- My Conference History ----------------

@router.get(
    "/my",
    response_model=list[schemas.ConferenceRegistrationResponse]
)

def my_conference_history(

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):


    researcher = db.query(
        models.Researcher
    ).filter(
        models.Researcher.user_id == current_user.id
    ).first()



    if not researcher:

        raise HTTPException(
            status_code=404,
            detail="Researcher profile not found"
        )



    return crud.get_registrations_by_researcher(

        db,

        researcher.id

    )





# ---------------- Conference Participants ----------------

@router.get(
    "/conference/{conference_id}",
    response_model=list[schemas.ConferenceRegistrationResponse]
)

def conference_participants(

    conference_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):


    return crud.get_conference_participants(

        db,

        conference_id

    )





# ---------------- Cancel Registration ----------------

@router.delete(
    "/{registration_id}"
)

def cancel_registration(

    registration_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):


    deleted = crud.delete_conference_registration(

        db,

        registration_id

    )


    if not deleted:

        raise HTTPException(

            status_code=404,

            detail="Registration not found"

        )


    return {

        "message":
        "Conference registration cancelled successfully"

    }