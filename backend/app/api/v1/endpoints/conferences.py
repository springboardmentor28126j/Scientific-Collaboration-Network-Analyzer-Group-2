from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select, desc, asc, func, or_, exists
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.conference import Conference, ConferenceParticipation, ParticipationRole, SubmissionStatus, ConferenceStatus
from app.models.institution import Institution
from app.models.researcher import ResearcherProfile
from app.models.user import User, UserRole
from app.schemas.conference import (
    ConferenceCreate, ConferenceUpdate, ConferenceOut, ConferenceListResponse,
    ParticipationCreate, ParticipationUpdate, ParticipationOut,
)
from app.utils.audit import write_audit_log
from app.utils.notifications import notify

router = APIRouter(prefix="/conferences", tags=["Conferences"])

ALLOWED_PAGE_SIZES = {10, 25, 50}


def _require_own_institution_conference(current_user: User, conference: Conference) -> None:
    """
    System admins can touch any conference. Institution admins may only
    manage conferences organized by their own institution (BR: "Institution
    Admin: Conference created by institution: CRUD").
    """
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return
    if current_user.role != UserRole.INSTITUTION_ADMIN or conference.organizing_institution_id != current_user.institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the organizing institution's admin (or a system admin) can manage this conference",
        )


@router.get("", response_model=ConferenceListResponse)
def list_conferences(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, description="Must be 10, 25, or 50"),
    status_filter: str | None = Query(None, alias="status"),
    institution_id: int | None = Query(None),
    author_id: int | None = Query(None, description="Filter to conferences this researcher participated in/presented at"),
    year: int | None = Query(None, description="Filter to conferences taking place in this year"),
    q: str | None = Query(None, description="Search across name, location, institution name, presenter name, and year"),
    sort_by: str = Query("date", description="'date' or 'name'"),
    sort_dir: str = Query("desc", description="'asc' or 'desc'"),
    mine: bool = Query(False, description="Only conferences I'm registered for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if page_size not in ALLOWED_PAGE_SIZES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"page_size must be one of {sorted(ALLOWED_PAGE_SIZES)}",
        )
    if sort_by not in ("date", "name"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="sort_by must be 'date' or 'name'")
    if sort_dir not in ("asc", "desc"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="sort_dir must be 'asc' or 'desc'")

    stmt = select(Conference)
    if status_filter:
        stmt = stmt.where(Conference.status == status_filter)
    if institution_id:
        stmt = stmt.where(Conference.organizing_institution_id == institution_id)
    if author_id:
        stmt = stmt.where(
            exists(
                select(1).select_from(ConferenceParticipation).where(
                    ConferenceParticipation.conference_id == Conference.conference_id,
                    ConferenceParticipation.researcher_id == author_id,
                )
            )
        )
    if year:
        stmt = stmt.where(Conference.start_date >= date(year, 1, 1), Conference.start_date < date(year + 1, 1, 1))
    if mine:
        profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
        if profile is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You don't have a researcher profile yet")
        stmt = stmt.where(
            exists(
                select(1).select_from(ConferenceParticipation).where(
                    ConferenceParticipation.conference_id == Conference.conference_id,
                    ConferenceParticipation.researcher_id == profile.researcher_id,
                )
            )
        )
    if q:
        term = f"%{q}%"
        name_match = or_(ResearcherProfile.first_name.ilike(term), ResearcherProfile.last_name.ilike(term))
        presenter_match = exists(
            select(1)
            .select_from(ConferenceParticipation)
            .join(ResearcherProfile, ResearcherProfile.researcher_id == ConferenceParticipation.researcher_id)
            .where(ConferenceParticipation.conference_id == Conference.conference_id, name_match)
        )
        institution_match = exists(
            select(1).select_from(Institution).where(
                Institution.institution_id == Conference.organizing_institution_id, Institution.name.ilike(term)
            )
        )
        conditions = [
            Conference.name.ilike(term),
            Conference.location.ilike(term),
            presenter_match,
            institution_match,
        ]
        stripped = q.strip()
        if stripped.isdigit() and len(stripped) == 4:
            yr = int(stripped)
            conditions.append(
                (Conference.start_date >= date(yr, 1, 1)) & (Conference.start_date < date(yr + 1, 1, 1))
            )
        stmt = stmt.where(or_(*conditions))

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    order_column = Conference.name if sort_by == "name" else Conference.start_date
    order_fn = asc if sort_dir == "asc" else desc
    stmt = stmt.order_by(order_fn(order_column)).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(stmt).all())

    return ConferenceListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{conference_id}", response_model=ConferenceOut)
def get_conference(conference_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conference = db.get(Conference, conference_id)
    if conference is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    return conference


@router.post("", response_model=ConferenceOut, status_code=status.HTTP_201_CREATED)
def create_conference(
    payload: ConferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
):
    if payload.end_date < payload.start_date:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="end_date cannot be before start_date")

    if current_user.role == UserRole.INSTITUTION_ADMIN:
        # An institution admin can only organize conferences under their own
        # institution -- ignore/override anything else supplied in the payload.
        if payload.organizing_institution_id not in (None, current_user.institution_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create conferences organized by your own institution",
            )
        payload = payload.model_copy(update={"organizing_institution_id": current_user.institution_id})

    conference = Conference(**payload.model_dump())
    db.add(conference)
    db.commit()
    db.refresh(conference)
    write_audit_log(db, current_user.user_id, "CREATE", "conference", conference.conference_id)
    return conference


@router.patch("/{conference_id}", response_model=ConferenceOut)
def update_conference(
    conference_id: int, payload: ConferenceUpdate, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
):
    conference = db.get(Conference, conference_id)
    if conference is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    _require_own_institution_conference(current_user, conference)

    update_data = payload.model_dump(exclude_unset=True)
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        # Can't hand the conference off to a different institution.
        update_data.pop("organizing_institution_id", None)

    for field, value in update_data.items():
        setattr(conference, field, value)
    db.commit()
    db.refresh(conference)
    write_audit_log(db, current_user.user_id, "UPDATE", "conference", conference.conference_id)
    return conference


@router.delete("/{conference_id}", status_code=204)
def delete_conference(
    conference_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
):
    conference = db.get(Conference, conference_id)
    if conference is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    _require_own_institution_conference(current_user, conference)

    write_audit_log(db, current_user.user_id, "DELETE", "conference", conference_id)
    db.delete(conference)
    db.commit()
    return None


@router.get("/{conference_id}/participants/{participation_id}/certificate")
def download_certificate(
    conference_id: int, participation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    participation = db.get(ConferenceParticipation, participation_id)
    if participation is None or participation.conference_id != conference_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participation not found")

    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    is_owner = profile is not None and participation.researcher_id == profile.researcher_id
    conference = db.get(Conference, conference_id)
    if not is_owner and not _is_conference_manager(current_user, conference):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot download another researcher's certificate")

    eligible = participation.submission_status in (SubmissionStatus.ACCEPTED, SubmissionStatus.PUBLISHED) or (
        participation.role == ParticipationRole.ATTENDEE and conference.status == ConferenceStatus.COMPLETED
    )
    if not eligible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A certificate is only available once your submission is accepted, or after the conference has completed",
        )

    body = (
        "CERTIFICATE OF PARTICIPATION\n"
        "=============================\n\n"
        f"This certifies that {participation.researcher_name}\n"
        f"participated as {participation.role.value.title()}\n"
        f"in \"{conference.name}\"\n"
        f"held {conference.start_date} to {conference.end_date}"
        + (f" at {conference.location}" if conference.location else "") + ".\n\n"
        + (f"Presentation: {participation.presentation_title}\n\n" if participation.presentation_title else "")
        + "Issued by the Scientific Collaboration Analyzer platform.\n"
    )
    filename = f"certificate_conference_{conference_id}_participation_{participation_id}.txt"
    return Response(
        content=body, media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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

    if payload.role not in (ParticipationRole.ATTENDEE, ParticipationRole.PRESENTER):
        # Self-registering as Organizer or Reviewer would let anyone approve
        # their own (or others') submissions. Those roles are assigned by the
        # organizing institution's admin, not self-selected.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only self-register as attendee or presenter. Organizer/reviewer roles are assigned by the conference organizer.",
        )

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


def _is_conference_manager(current_user: User, conference: Conference | None) -> bool:
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return True
    return (
        current_user.role == UserRole.INSTITUTION_ADMIN
        and conference is not None
        and conference.organizing_institution_id == current_user.institution_id
    )


@router.patch("/{conference_id}/participants/{participation_id}", response_model=ParticipationOut)
def update_participation(
    conference_id: int, participation_id: int, payload: ParticipationUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    participation = db.get(ConferenceParticipation, participation_id)
    if participation is None or participation.conference_id != conference_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participation not found")

    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    is_owner = profile is not None and participation.researcher_id == profile.researcher_id
    conference = db.get(Conference, conference_id)
    is_manager = _is_conference_manager(current_user, conference)

    if not is_owner and not is_manager:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit another researcher's participation")

    update_data = payload.model_dump(exclude_unset=True)

    if "submission_status" in update_data and not is_manager:
        # BR: Researcher "Cannot: Approve Conference". A researcher may only
        # submit their own draft for review -- everything past that (under
        # review / accepted / rejected / published) is a review decision made
        # by the organizing institution admin (or system admin).
        new_status = update_data["submission_status"]
        allowed = participation.submission_status == SubmissionStatus.DRAFT and new_status == SubmissionStatus.SUBMITTED
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only move your own submission from draft to submitted. Review decisions are made by the organizing institution.",
            )

    if "role" in update_data and not is_manager and update_data["role"] not in (ParticipationRole.ATTENDEE, ParticipationRole.PRESENTER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the conference organizer can assign the organizer or reviewer role",
        )

    for field, value in update_data.items():
        setattr(participation, field, value)
    db.commit()
    db.refresh(participation)
    write_audit_log(db, current_user.user_id, "UPDATE", "conference_participation", participation.participation_id)
    if "submission_status" in update_data:
        owner_profile = db.get(ResearcherProfile, participation.researcher_id)
        owner_user_id = owner_profile.user_id if owner_profile else None
        if owner_user_id is not None and owner_user_id != current_user.user_id:
            notify(
                db, owner_user_id, "conference_submission_status_changed", "Conference submission status updated",
                f"Your submission status for the conference is now: {participation.submission_status.value.replace('_', ' ')}.",
                link_url=f"/conferences/{conference_id}",
            )
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
