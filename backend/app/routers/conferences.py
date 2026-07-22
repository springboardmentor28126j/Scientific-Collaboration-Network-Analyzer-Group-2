from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.conference import Conference, ConferenceParticipation
from app.schemas.conference import ConferenceCreate, ConferenceOut, ParticipationCreate, ParticipationOut

router = APIRouter()


@router.post("/", response_model=ConferenceOut)
def create_conference(conference: ConferenceCreate, db: Session = Depends(get_db)):
    new_conf = Conference(**conference.dict())
    db.add(new_conf)
    db.commit()
    db.refresh(new_conf)
    return new_conf


@router.get("/", response_model=List[ConferenceOut])
def list_conferences(db: Session = Depends(get_db)):
    return db.query(Conference).all()


@router.get("/{conference_id}", response_model=ConferenceOut)
def get_conference(conference_id: int, db: Session = Depends(get_db)):
    conf = db.query(Conference).filter(Conference.id == conference_id).first()
    if not conf:
        raise HTTPException(status_code=404, detail="Conference not found")
    return conf


@router.delete("/{conference_id}")
def delete_conference(conference_id: int, db: Session = Depends(get_db)):
    conf = db.query(Conference).filter(Conference.id == conference_id).first()
    if not conf:
        raise HTTPException(status_code=404, detail="Conference not found")
    db.delete(conf)
    db.commit()
    return {"message": "Conference deleted successfully"}


@router.post("/participate", response_model=ParticipationOut)
def register_participation(participation: ParticipationCreate, db: Session = Depends(get_db)):
    new_participation = ConferenceParticipation(**participation.dict())
    db.add(new_participation)
    db.commit()
    db.refresh(new_participation)
    return new_participation