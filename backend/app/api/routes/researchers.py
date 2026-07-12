from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.researcher_profile import (
    get_or_create_profile,
    get_profile_by_user_id,
    list_profiles,
    update_profile,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.researcher_profile import ResearcherProfileRead, ResearcherProfileUpdate

router = APIRouter(prefix="/researchers", tags=["Researcher Profiles"])


@router.get("/me", response_model=ResearcherProfileRead)
def read_my_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return get_or_create_profile(db, current_user.id)


@router.put("/me", response_model=ResearcherProfileRead)
def update_my_profile(
    profile_in: ResearcherProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_profile(db, current_user.id)
    return update_profile(db, profile, profile_in)


@router.get("/", response_model=list[ResearcherProfileRead])
def read_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return list_profiles(db, skip, limit)


@router.get("/{user_id}", response_model=ResearcherProfileRead)
def read_profile(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile
