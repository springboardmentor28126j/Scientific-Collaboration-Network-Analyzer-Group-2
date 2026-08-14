from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from typing import List, Optional
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

    # Audit log
    from app.models.audit_log import AuditLog
    log = AuditLog(user_id=1, action="create_conference", details=f"Created conference: {new_conf.name}")
    db.add(log)
    db.commit()

    return new_conf


@router.get("/")
def list_conferences(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("id", regex="^(id|name|start_date|location)$"),
    order: str = Query("desc", regex="^(asc|desc)$")
):
    query = db.query(Conference)

    sort_column = getattr(Conference, sort_by)
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    total = query.count()
    offset = (page - 1) * limit
    conferences = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "conferences": conferences
    }


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

    conf_name = conf.name

    db.delete(conf)
    db.commit()

    # Audit log
    from app.models.audit_log import AuditLog
    log = AuditLog(user_id=1, action="delete_conference", details=f"Deleted conference: {conf_name}")
    db.add(log)
    db.commit()

    return {"message": "Conference deleted successfully"}


@router.post("/participate", response_model=ParticipationOut)
def register_participation(participation: ParticipationCreate, db: Session = Depends(get_db)):
    new_participation = ConferenceParticipation(**participation.dict())
    db.add(new_participation)
    db.commit()
    db.refresh(new_participation)
    return new_participation