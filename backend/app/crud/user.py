from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.researcher_profile import ResearcherProfile
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return list(db.execute(select(User).offset(skip).limit(limit)).scalars())


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
        role=user_in.role,
        institution_id=user_in.institution_id,
    )
    db.add(user)
    db.flush()

    if user.role == UserRole.RESEARCHER:
        db.add(ResearcherProfile(user_id=user.id))

    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
