from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.institution import Institution
from app.models.participation import ConferenceParticipation
from app.models.publication import Publication, PublicationAuthor
from app.models.researcher import Researcher
from app.models.user import User
from app.schemas.conference import ParticipationWithConference
from app.schemas.publication import PublicationOut
from app.schemas.researcher import ResearcherCreate, ResearcherOut, ResearcherUpdate

router = APIRouter()


def _get_or_none(db: Session, user_id: int) -> Researcher | None:
    return db.query(Researcher).filter(Researcher.user_id == user_id).first()


def _validate_institution_id(db: Session, institution_id: int | None) -> None:
    if institution_id is None:
        return
    exists = db.query(Institution).filter(Institution.id == institution_id).first()
    if exists is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Institution {institution_id} not found",
        )


@router.get("/me", response_model=ResearcherOut)
def get_my_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Researcher:
    researcher = _get_or_none(db, current_user.id)
    if researcher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Researcher profile not found"
        )
    return researcher


@router.post("/me", response_model=ResearcherOut, status_code=status.HTTP_201_CREATED)
def create_my_profile(
    payload: ResearcherCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Researcher:
    if _get_or_none(db, current_user.id) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Researcher profile already exists — use PUT to update it",
        )
    _validate_institution_id(db, payload.institution_id)

    researcher = Researcher(user_id=current_user.id, **payload.model_dump())
    db.add(researcher)
    db.commit()
    db.refresh(researcher)
    return researcher


@router.put("/me", response_model=ResearcherOut)
def update_my_profile(
    payload: ResearcherUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Researcher:
    researcher = _get_or_none(db, current_user.id)
    if researcher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Researcher profile not found"
        )
    _validate_institution_id(db, payload.institution_id)

    for field, value in payload.model_dump().items():
        setattr(researcher, field, value)

    db.commit()
    db.refresh(researcher)
    return researcher


@router.get("", response_model=list[ResearcherOut])
def list_researchers(
    institution_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Researcher]:
    query = db.query(Researcher)
    if institution_id is not None:
        query = query.filter(Researcher.institution_id == institution_id)
    return query.order_by(Researcher.id).all()


@router.get("/search", response_model=list[ResearcherOut])
def search_researchers(
    q: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Researcher]:
    like = f"%{q}%"
    return (
        db.query(Researcher)
        .filter(
            or_(
                Researcher.department.ilike(like),
                Researcher.research_interests.ilike(like),
                Researcher.skills.ilike(like),
                Researcher.affiliations.ilike(like),
            )
        )
        .order_by(Researcher.id)
        .all()
    )


@router.get("/{researcher_id}", response_model=ResearcherOut)
def get_researcher(
    researcher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Researcher:
    researcher = db.query(Researcher).filter(Researcher.id == researcher_id).first()
    if researcher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Researcher not found"
        )
    return researcher


@router.get("/{researcher_id}/publications", response_model=list[PublicationOut])
def get_researcher_publications(
    researcher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Publication]:
    if db.query(Researcher).filter(Researcher.id == researcher_id).first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Researcher not found"
        )
    return (
        db.query(Publication)
        .options(selectinload(Publication.authors))
        .join(PublicationAuthor)
        .filter(PublicationAuthor.researcher_id == researcher_id)
        .order_by(Publication.year.desc().nullslast(), Publication.id.desc())
        .all()
    )


@router.get(
    "/{researcher_id}/conferences", response_model=list[ParticipationWithConference]
)
def get_researcher_conferences(
    researcher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConferenceParticipation]:
    if db.query(Researcher).filter(Researcher.id == researcher_id).first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Researcher not found"
        )
    return (
        db.query(ConferenceParticipation)
        .options(selectinload(ConferenceParticipation.conference))
        .filter(ConferenceParticipation.researcher_id == researcher_id)
        .order_by(ConferenceParticipation.id.desc())
        .all()
    )