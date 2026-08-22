from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.institution import Institution
from app.models.researcher import Researcher
from app.models.user import User
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
