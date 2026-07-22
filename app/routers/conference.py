from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import schemas, crud, models
from app.oauth2 import get_current_user
from app.models import User


router = APIRouter(
    prefix="/conferences",
    tags=["Conferences"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# ---------------- Create Conference ----------------
# Only Institution Admin and System Admin can create

@router.post("/", response_model=schemas.ConferenceResponse)
def create_conference(
    conference: schemas.ConferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role not in [
        "institution_admin",
        "system_admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Only Institution Admin and System Admin can create conferences"
        )


    return crud.create_conference(
        db,
        conference
    )



# ---------------- View Conferences ----------------
# All roles can view

@router.get("/", response_model=list[schemas.ConferenceResponse])
def get_all_conferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return crud.get_all_conferences(db)


@router.get("/my")
def get_my_conferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Researcher login
    researcher = db.query(models.Researcher).filter(
        models.Researcher.user_id == current_user.id
    ).first()


    if researcher:

        return db.query(models.Conference).filter(
            models.Conference.institution == researcher.institution
        ).all()



    # Institution Admin login
    institution = db.query(models.Institution).filter(
        models.Institution.user_id == current_user.id
    ).first()


    if institution:

        return db.query(models.Conference).filter(
            models.Conference.institution == institution.name
        ).all()



    raise HTTPException(
        status_code=404,
        detail="Institution not found"
    )
@router.get("/institution/{institution_name}")
def get_conferences_by_institution(
    institution_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conferences = db.query(models.Conference).filter(
        models.Conference.institution == institution_name
    ).all()

    return conferences
# ---------------- Get Single Conference ----------------

@router.get("/{conference_id}", response_model=schemas.ConferenceResponse)
def get_conference(
    conference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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




# ---------------- Update Conference ----------------
# Only Institution Admin and System Admin can update

@router.put("/{conference_id}", response_model=schemas.ConferenceResponse)
def update_conference(
    conference_id: int,
    conference: schemas.ConferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("UPDATE RECEIVED:")
    print(conference.model_dump())

    if current_user.role not in [
        "institution_admin",
        "system_admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Only Institution Admin and System Admin can update conferences"
        )


    updated = crud.update_conference(
        db,
        conference_id,
        conference
    )


    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Conference not found"
        )


    return updated





# ---------------- Delete Conference ----------------
# Only System Admin can delete

@router.delete("/{conference_id}")
def delete_conference(
    conference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "system_admin":

        raise HTTPException(
            status_code=403,
            detail="Only System Admin can delete conferences"
        )


    deleted = crud.delete_conference(
        db,
        conference_id
    )


    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conference not found"
        )


    return {
        "message": "Conference deleted successfully"
    }