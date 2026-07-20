from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import schemas, crud
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


@router.post("/", response_model=schemas.ConferenceResponse)
def create_conference(
    conference: schemas.ConferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.create_conference(db, conference)


@router.get("/", response_model=list[schemas.ConferenceResponse])
def get_all_conferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_all_conferences(db)


@router.get("/{conference_id}", response_model=schemas.ConferenceResponse)
def get_conference(
    conference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conference = crud.get_conference_by_id(db, conference_id)

    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")

    return conference


@router.put("/{conference_id}", response_model=schemas.ConferenceResponse)
def update_conference(
    conference_id: int,
    conference: schemas.ConferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = crud.update_conference(db, conference_id, conference)

    if not updated:
        raise HTTPException(status_code=404, detail="Conference not found")

    return updated


@router.delete("/{conference_id}")
def delete_conference(
    conference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = crud.delete_conference(db, conference_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Conference not found")

    return {"message": "Conference deleted successfully"}