from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/conferences",
    tags=["Conferences"]
)

@router.post("/", response_model=schemas.ConferenceResponse)
def create_conference(conference: schemas.ConferenceCreate, db: Session = Depends(get_db)):
    return crud.create_conference(db, conference)

@router.get("/", response_model=list[schemas.ConferenceResponse])
def get_conferences(db: Session = Depends(get_db)):
    return crud.get_conferences(db)

@router.get("/{conference_id}", response_model=schemas.ConferenceResponse)
def get_conference(conference_id: int, db: Session = Depends(get_db)):
    conf = crud.get_conference_by_id(db, conference_id)
    if not conf:
        raise HTTPException(status_code=404, detail="Conference not found")
    return conf

@router.post("/participation", response_model=schemas.ConferenceParticipationResponse)
def register_participation(participation: schemas.ConferenceParticipationCreate, db: Session = Depends(get_db)):
    return crud.register_participation(db, participation)


@router.get("/{conference_id}/participants", response_model=list[schemas.ConferenceParticipationResponse])
def get_participants(conference_id: int, db: Session = Depends(get_db)):
    return crud.get_participants_by_conference(db, conference_id)


@router.get("/researcher/{researcher_id}", response_model=list[schemas.ConferenceParticipationResponse])
def get_conferences_for_researcher(researcher_id: int, db: Session = Depends(get_db)):
    return crud.get_conferences_by_researcher(db, researcher_id)
