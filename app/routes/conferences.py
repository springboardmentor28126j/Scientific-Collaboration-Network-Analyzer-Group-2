from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, auth
from app.database import get_db
from app.notification_service import notify_all_users
from app.permissions import require_roles
from app.audit import record as record_audit

router = APIRouter(
    prefix="/conferences",
    tags=["Conferences"],
    dependencies=[Depends(auth.require_authenticated)]
)

@router.post("/", response_model=schemas.ConferenceResponse)
def create_conference(conference: schemas.ConferenceCreate, manager: models.User = Depends(require_roles("admin", "system admin", "institution admin")), db: Session = Depends(get_db)):
    created = crud.create_conference(db, conference)
    record_audit(db, action="created", entity_type="conference", entity_id=created.id, user_id=manager.id, details=created.name)
    notify_all_users(db, notification_type="conference", title="New conference scheduled", message=f"{created.name} was added to the conference calendar.", link="pages/conferences.html")
    return created

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
def register_participation(participation: schemas.ConferenceParticipationCreate, manager: models.User = Depends(require_roles("admin", "system admin", "institution admin", "researcher")), db: Session = Depends(get_db)):
    created = crud.register_participation(db, participation)
    record_audit(db, action="registered", entity_type="conference", entity_id=participation.conference_id, user_id=manager.id, details=f"Researcher {participation.researcher_id}")
    return created


@router.get("/{conference_id}/participants", response_model=list[schemas.ConferenceParticipationResponse])
def get_participants(conference_id: int, db: Session = Depends(get_db)):
    return crud.get_participants_by_conference(db, conference_id)


@router.get("/researcher/{researcher_id}", response_model=list[schemas.ConferenceParticipationResponse])
def get_conferences_for_researcher(researcher_id: int, db: Session = Depends(get_db)):
    return crud.get_conferences_by_researcher(db, researcher_id)
