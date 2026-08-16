from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.conference import Conference, ConferenceParticipation
from app.models.researcher import ResearcherProfile
from app.models.user import User
from app.schemas.conference import (
    ConferenceCreate, ConferenceUpdate, ConferenceOut,
    ParticipationCreate, ParticipationUpdate, ParticipationOut,
)
from app.utils.audit import write_audit_log

router = APIRouter(prefix="/conferences", tags=["Conferences"])


@router.get("", response_model=list[ConferenceOut])
def list_conferences(
    status_filter: str | None = Query(None, alias="status"),
    institution_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Conference)
    if status_filter:
        stmt = stmt.where(Conference.status == status_filter)
    if institution_id:
        stmt = stmt.where(Conference.organizing_institution_id == institution_id)
    stmt = stmt.order_by(desc(Conference.start_date)).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get("/{conference_id}", response_model=ConferenceOut)
def get_conference(conference_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conference = db.get(Conference, conference_id)
    if conference is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    return conference


@router.post("", response_model=ConferenceOut, status_code=status.HTTP_201_CREATED)
def create_conference(payload: ConferenceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.end_date < payload.start_date:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="end_date cannot be before start_date")

    conference = Conference(**payload.model_dump())
    db.add(conference)
    db.commit()
    db.refresh(conference)
    write_audit_log(db, current_user.user_id, "CREATE", "conference", conference.conference_id)
    return conference


@router.patch("/{conference_id}", response_model=ConferenceOut)
def update_conference(
    conference_id: int, payload: ConferenceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    conference = db.get(Conference, conference_id)
    if conference is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(conference, field, value)
    db.commit()
    db.refresh(conference)
    write_audit_log(db, current_user.user_id, "UPDATE", "conference", conference.conference_id)
    return conference


@router.delete("/{conference_id}", status_code=204)
def delete_conference(conference_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conference = db.get(Conference, conference_id)
    if conference is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")

    write_audit_log(db, current_user.user_id, "DELETE", "conference", conference_id)
    db.delete(conference)
    db.commit()
    return None


# --- Participation ---

@router.get("/{conference_id}/participants", response_model=list[ParticipationOut])
def list_participants(conference_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(ConferenceParticipation).where(ConferenceParticipation.conference_id == conference_id)
    return list(db.scalars(stmt).all())


@router.post("/{conference_id}/register", response_model=ParticipationOut, status_code=status.HTTP_201_CREATED)
def register_participation(
    conference_id: int, payload: ParticipationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    conference = db.get(Conference, conference_id)
    if conference is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")

    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need a researcher profile before registering for a conference",
        )

    existing = db.scalar(
        select(ConferenceParticipation).where(
            ConferenceParticipation.conference_id == conference_id,
            ConferenceParticipation.researcher_id == profile.researcher_id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already registered for this conference (one role per researcher per conference)",
        )

    participation = ConferenceParticipation(
        conference_id=conference_id,
        researcher_id=profile.researcher_id,
        **payload.model_dump(),
    )
    db.add(participation)
    db.commit()
    db.refresh(participation)
    write_audit_log(db, current_user.user_id, "CREATE", "conference_participation", participation.participation_id)
    return participation


@router.patch("/{conference_id}/participants/{participation_id}", response_model=ParticipationOut)
def update_participation(
    conference_id: int, participation_id: int, payload: ParticipationUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    participation = db.get(ConferenceParticipation, participation_id)
    if participation is None or participation.conference_id != conference_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participation not found")

    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    if profile is None or participation.researcher_id != profile.researcher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit another researcher's participation")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(participation, field, value)
    db.commit()
    db.refresh(participation)
    write_audit_log(db, current_user.user_id, "UPDATE", "conference_participation", participation.participation_id)
    return participation


@router.delete("/{conference_id}/participants/{participation_id}", status_code=204)
def cancel_participation(
    conference_id: int, participation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    participation = db.get(ConferenceParticipation, participation_id)
    if participation is None or participation.conference_id != conference_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participation not found")

    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    if profile is None or participation.researcher_id != profile.researcher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot cancel another researcher's participation")

    write_audit_log(db, current_user.user_id, "DELETE", "conference_participation", participation_id)
    db.delete(participation)
    db.commit()
    return None
