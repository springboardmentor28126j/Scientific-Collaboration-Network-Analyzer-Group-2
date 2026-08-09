from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.conference import Conference
from app.models.institution import Institution
from app.models.participation import ConferenceParticipation, ParticipationStatus
from app.models.researcher import Researcher
from app.models.user import User, UserRole
from app.models.session import ConferenceSession
from app.schemas.conference import (
    ConferenceCreate,
    ConferenceOut,
    ConferenceUpdate,
    ParticipationCreate,
    ParticipationOut,
    ParticipationRoleUpdate,
    ParticipationStatusUpdate,
    ParticipationWithConference,
)
from app.schemas.session import SessionCreate, SessionOut

router = APIRouter()
UPLOAD_DIR = Path("uploads/conference_presentations")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".pdf", ".ppt", ".pptx", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def _get_conference_or_404(db: Session, conference_id: int) -> Conference:
    conference = db.query(Conference).filter(Conference.id == conference_id).first()
    if conference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found"
        )
    return conference


def _get_my_researcher_or_400(db: Session, user_id: int) -> Researcher:
    researcher = db.query(Researcher).filter(Researcher.user_id == user_id).first()
    if researcher is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create your researcher profile before registering for a conference",
        )
    return researcher


def _is_conference_organizer(db: Session, user: User, conference: Conference) -> bool:
    """True if `user` has real organizer authority over this conference:
    they created it, they're the System Admin, or they're the Institution
    Admin of the institution hosting it."""
    if user.role == UserRole.SYSTEM_ADMIN:
        return True
    if conference.created_by is not None and conference.created_by == user.id:
        return True
    if user.role == UserRole.INSTITUTION_ADMIN and conference.institution_id is not None:
        institution = (
            db.query(Institution).filter(Institution.id == conference.institution_id).first()
        )
        if institution is not None and institution.admin_user_id == user.id:
            return True
    return False

def _validate_session_dates(conference: Conference, payload: SessionCreate) -> None:
    if payload.end_time is not None and payload.end_time <= payload.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session end time must be after the start time.",
        )

    if conference.start_date is None:
        # Conference has no dates set yet, nothing to validate the session against.
        return

    conf_end_date = conference.end_date or conference.start_date
    session_start_date = payload.start_time.date()
    session_end_date = (payload.end_time or payload.start_time).date()

    if session_start_date < conference.start_date or session_end_date > conf_end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"This session falls outside the conference dates "
                f"({conference.start_date} to {conf_end_date}). "
                "Update the conference's start/end date first, or pick a session "
                "time within that range."
            ),
        )


def _check_duplicate_session(
    db: Session, conference_id: int, payload: SessionCreate
) -> None:
    duplicate = (
        db.query(ConferenceSession)
        .filter(
            ConferenceSession.conference_id == conference_id,
            ConferenceSession.start_time == payload.start_time,
        )
        .all()
    )
    for existing in duplicate:
        if existing.title.strip().lower() == payload.title.strip().lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A session with this title is already scheduled at this time.",
            )


@router.post("", response_model=ConferenceOut, status_code=status.HTTP_201_CREATED)
def create_conference(
    payload: ConferenceCreate,
    current_user: User = Depends(require_role(UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
) -> Conference:
    institution = (
        db.query(Institution).filter(Institution.id == payload.institution_id).first()
    )
    if institution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    if (
        current_user.role != UserRole.SYSTEM_ADMIN
        and institution.admin_user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create conferences for an institution you administer",
        )

    conference = Conference(created_by=current_user.id, **payload.model_dump())
    db.add(conference)
    db.commit()
    db.refresh(conference)
    return conference


@router.get("", response_model=list[ConferenceOut])
def list_conferences(
    q: str | None = None,
    year: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Conference]:
    query = db.query(Conference)
    if q:
        query = query.filter(Conference.name.ilike(f"%{q}%"))
    if year:
        query = query.filter(extract("year", Conference.start_date) == year)
    return query.order_by(Conference.start_date).all()


@router.get("/{conference_id}", response_model=ConferenceOut)
def get_conference(
    conference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Conference:
    return _get_conference_or_404(db, conference_id)


@router.put("/{conference_id}", response_model=ConferenceOut)
def update_conference(
    conference_id: int,
    payload: ConferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Conference:
    conference = _get_conference_or_404(db, conference_id)
    if conference.created_by is not None and conference.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can update this conference",
        )
    for field, value in payload.model_dump().items():
        setattr(conference, field, value)
    db.commit()
    db.refresh(conference)
    return conference


@router.post(
    "/{conference_id}/register",
    response_model=ParticipationOut,
    status_code=status.HTTP_201_CREATED,
)
def register_for_conference(
    conference_id: int,
    payload: ParticipationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConferenceParticipation:
    _get_conference_or_404(db, conference_id)
    researcher = _get_my_researcher_or_400(db, current_user.id)

    existing = (
        db.query(ConferenceParticipation)
        .filter(
            ConferenceParticipation.researcher_id == researcher.id,
            ConferenceParticipation.conference_id == conference_id,
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already registered for this conference",
        )

    participation = ConferenceParticipation(
        researcher_id=researcher.id, conference_id=conference_id, **payload.model_dump()
    )
    db.add(participation)
    db.commit()
    db.refresh(participation)
    return participation

@router.patch("/participations/{participation_id}/status", response_model=ParticipationOut)
def update_participation_status(
    participation_id: int,
    payload: ParticipationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConferenceParticipation:
    participation = (
        db.query(ConferenceParticipation)
        .filter(ConferenceParticipation.id == participation_id)
        .first()
    )
    if participation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participation record not found"
        )

    researcher = _get_my_researcher_or_400(db, current_user.id)
    conference = _get_conference_or_404(db, participation.conference_id)

    is_owner = participation.researcher_id == researcher.id
    is_organizer = _is_conference_organizer(db, current_user, conference)

    if not is_owner and not is_organizer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the registrant or the conference organizer can update this status",
        )

    if is_owner and not is_organizer and payload.status != ParticipationStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own registration",
        )

    participation.status = payload.status
    db.commit()
    db.refresh(participation)
    return participation


@router.patch("/participations/{participation_id}/role", response_model=ParticipationOut)
def update_participation_role(
    participation_id: int,
    payload: ParticipationRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConferenceParticipation:
    """Promote/demote a registrant's role for this conference (e.g. to
    Organizer or Reviewer). Unlike self-registration, this isn't
    self-service: only the conference's real organizer may call it."""
    participation = (
        db.query(ConferenceParticipation)
        .filter(ConferenceParticipation.id == participation_id)
        .first()
    )
    if participation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participation record not found"
        )

    conference = _get_conference_or_404(db, participation.conference_id)
    if not _is_conference_organizer(db, current_user, conference):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the conference organizer can change a participant's role",
        )

    participation.role = payload.role
    db.commit()
    db.refresh(participation)
    return participation

@router.get("/{conference_id}/participants", response_model=list[ParticipationOut])
def list_participants(
    conference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ConferenceParticipation]:
    _get_conference_or_404(db, conference_id)
    return (
        db.query(ConferenceParticipation)
        .filter(ConferenceParticipation.conference_id == conference_id)
        .all()
    )


@router.get("/me/history", response_model=list[ParticipationWithConference])
def my_participation_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConferenceParticipation]:
    researcher = _get_my_researcher_or_400(db, current_user.id)
    return (
        db.query(ConferenceParticipation)
        .filter(ConferenceParticipation.researcher_id == researcher.id)
        .all()
    )

@router.post("/participations/{participation_id}/upload", response_model=ParticipationOut)
async def upload_presentation_file(
    participation_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConferenceParticipation:
    participation = (
        db.query(ConferenceParticipation)
        .filter(ConferenceParticipation.id == participation_id)
        .first()
    )
    if participation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participation record not found"
        )

    researcher = _get_my_researcher_or_400(db, current_user.id)
    if participation.researcher_id != researcher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload files for your own registration",
        )

    original_name = file.filename or "upload"
    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10 MB",
        )

    stored_filename = f"{participation_id}_{uuid4().hex}{ext}"
    (UPLOAD_DIR / stored_filename).write_bytes(contents)

    participation.stored_filename = stored_filename
    participation.original_filename = original_name
    db.commit()
    db.refresh(participation)
    return participation

def _attach_speaker_info(db: Session, session_obj: ConferenceSession) -> ConferenceSession:
    if session_obj.speaker_participation_id:
        participation = (
            db.query(ConferenceParticipation)
            .filter(ConferenceParticipation.id == session_obj.speaker_participation_id)
            .first()
        )
        if participation is not None:
            researcher = (
                db.query(Researcher).filter(Researcher.id == participation.researcher_id).first()
            )
            if researcher is not None:
                user = db.query(User).filter(User.id == researcher.user_id).first()
                if user is not None:
                    session_obj.speaker_email = user.email
            session_obj.speaker_role = participation.role.value
    return session_obj


@router.post(
    "/{conference_id}/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED
)
def create_session(
    conference_id: int,
    payload: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConferenceSession:
    conference = _get_conference_or_404(db, conference_id)

    _validate_session_dates(conference, payload)
    _check_duplicate_session(db, conference_id, payload)

    if payload.speaker_participation_id is not None:
        speaker = (
            db.query(ConferenceParticipation)
            .filter(
                ConferenceParticipation.id == payload.speaker_participation_id,
                ConferenceParticipation.conference_id == conference_id,
            )
            .first()
        )
        if speaker is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="speaker_participation_id must be a registration for this conference",
            )

    session_obj = ConferenceSession(conference_id=conference_id, **payload.model_dump())
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return _attach_speaker_info(db, session_obj)


@router.get("/{conference_id}/sessions", response_model=list[SessionOut])
def list_sessions(
    conference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ConferenceSession]:
    _get_conference_or_404(db, conference_id)
    sessions = (
        db.query(ConferenceSession)
        .filter(ConferenceSession.conference_id == conference_id)
        .order_by(ConferenceSession.start_time)
        .all()
    )
    return [_attach_speaker_info(db, s) for s in sessions]