from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.researcher_profile import ResearcherProfile
from app.schemas.researcher_profile import ResearcherProfileUpdate


def get_profile_by_user_id(db: Session, user_id: int) -> ResearcherProfile | None:
    return db.execute(
        select(ResearcherProfile).where(ResearcherProfile.user_id == user_id)
    ).scalar_one_or_none()


def get_or_create_profile(db: Session, user_id: int) -> ResearcherProfile:
    profile = get_profile_by_user_id(db, user_id)
    if profile is None:
        profile = ResearcherProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def list_profiles(db: Session, skip: int = 0, limit: int = 100) -> list[ResearcherProfile]:
    return list(db.execute(select(ResearcherProfile).offset(skip).limit(limit)).scalars())


def update_profile(
    db: Session, profile: ResearcherProfile, profile_in: ResearcherProfileUpdate
) -> ResearcherProfile:
    for field, value in profile_in.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
