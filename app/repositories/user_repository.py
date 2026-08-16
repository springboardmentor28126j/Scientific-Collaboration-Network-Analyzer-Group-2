from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

def get_by_google_sub(db: Session, google_sub: str) -> User | None:
    return db.query(User).filter(User.google_sub == google_sub).first()

def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def list_users(
    db: Session,
    institution_id: int | None = None,
    role: UserRole | None = None,
    page: int = 1,
    page_size: int = 20,
) -> list[User]:
    query = select(User)
    if institution_id is not None:
        query = query.where(User.institution_id == institution_id)
    if role is not None:
        query = query.where(User.role == role)
    query = query.offset((page - 1) * page_size).limit(page_size)
    return list(db.scalars(query).all())


def create_user(db: Session, email: str, password_hash: str, role: UserRole, institution_id: int | None) -> User:
    user = User(email=email, password_hash=password_hash, role=role, institution_id=institution_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
