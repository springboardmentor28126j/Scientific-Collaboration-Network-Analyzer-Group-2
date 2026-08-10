from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.researcher import Researcher
from app.models.user import User, UserRole
from app.schemas.user import Token, UserCreate, UserOut

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Self-registration only ever creates a Researcher account. Institution
    # Admin / Reviewer / System Admin accounts are granted by an existing
    # admin (see the admin user-management endpoints), never chosen by the
    # person signing up — the role on the incoming payload is ignored.
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.RESEARCHER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Every self-registered user gets an (initially empty) researcher profile
    # row so /researchers/me works immediately after signup.
    db.add(Researcher(user_id=user.id))
    db.commit()

    log_audit(
        db,
        user_id=user.id,
        action="register",
        entity_type="user",
        entity_id=user.id,
        details=f"email={user.email}",
    )
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> dict:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        log_audit(
            db,
            user_id=user.id if user else None,
            action="login_failed",
            entity_type="user",
            entity_id=user.id if user else None,
            details=f"email={form_data.username}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.email)
    log_audit(
        db, user_id=user.id, action="login", entity_type="user", entity_id=user.id
    )
    return {"access_token": access_token, "token_type": "bearer"}
