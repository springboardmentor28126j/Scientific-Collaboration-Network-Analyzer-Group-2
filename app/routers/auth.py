from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import SessionLocal

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate
)

from app import crud

from app.core.security import verify_password

from app.core.auth import (
    create_access_token,
    decode_access_token,
    oauth2_scheme
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================================
# DATABASE DEPENDENCY
# ==========================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================================
# REGISTER
# ==========================================

@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # Check whether email already exists
    existing_user = crud.get_user_by_email(
        db,
        user.email
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create new user
    return crud.create_user(
        db,
        user
    )


# ==========================================
# LOGIN - FRONTEND
# ==========================================
@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    # Find user
    db_user = crud.get_user_by_email(
        db,
        user.email
    )

    # User not found
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    password_valid = verify_password(
        user.password,
        db_user.hashed_password
    )

    # Wrong password
    if not password_valid:

        crud.create_audit_log(
            db=db,
            user_id=db_user.id,
            action="LOGIN_FAILED",
            module="Authentication",
            description=f"Failed login attempt for user {db_user.username}"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT token
    token = create_access_token(
        {
            "sub": db_user.email
        }
    )

    # Successful login audit
    crud.create_audit_log(
        db=db,
        user_id=db_user.id,
        action="LOGIN",
        module="Authentication",
        description=f"User {db_user.username} logged in successfully"
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": db_user.username,
        "full_name": db_user.full_name,
        "role": db_user.role
    }


# ==========================================
# LOGIN - SWAGGER / OAUTH2
# ==========================================

@router.post("/token")
def get_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # Swagger sends username field.
    # In our application username is the user's email.
    db_user = crud.get_user_by_email(
        db,
        form_data.username
    )

    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    password_valid = verify_password(
        form_data.password,
        db_user.hashed_password
    )

    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT token
    token = create_access_token(
        {
            "sub": db_user.email
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ==========================================
# CURRENT USER
# ==========================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    # Decode JWT
    payload = decode_access_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # Get email from JWT
    email = payload.get("sub")

    if not email:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # Find user
    user = crud.get_user_by_email(
        db,
        email
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# ==========================================
# UPDATE PROFILE
# ==========================================

@router.put(
    "/update-profile",
    response_model=UserResponse
)
def update_profile(
    updated_user: UserUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    # Decode JWT
    payload = decode_access_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # Get email from token
    email = payload.get("sub")

    if not email:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # Find logged-in user
    db_user = crud.get_user_by_email(
        db,
        email
    )

    if not db_user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Update profile
    # Update profile
    updated_profile = crud.update_user(
    db,
    db_user,
    updated_user
    )

# Create audit log
    crud.create_audit_log(
    db=db,
    user_id=db_user.id,
    action="PROFILE_UPDATED",
    module="User Profile",
    description=f"User {db_user.username} updated profile information"
    )

    return updated_profile