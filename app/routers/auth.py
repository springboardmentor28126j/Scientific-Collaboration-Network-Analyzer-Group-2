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
from app.services.captcha import (
    generate_captcha,
    verify_captcha
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
# CAPTCHA
# ==========================================

@router.get("/captcha")
def get_captcha():
    """
    Generate a new CAPTCHA challenge.
    """

    return generate_captcha()

# ==========================================
# LOGIN - FRONTEND + CAPTCHA
# ==========================================

@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    print("\n========== LOGIN DEBUG ==========")
    print("EMAIL:", user.email)
    print("CAPTCHA ID:", user.captcha_id)
    print("CAPTCHA ANSWER:", user.captcha_answer)

    # --------------------------------------
    # Verify CAPTCHA
    # --------------------------------------

    captcha_valid = verify_captcha(
        user.captcha_id,
        user.captcha_answer
    )

    print("CAPTCHA VALID:", captcha_valid)

    if not captcha_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired CAPTCHA"
        )

    # --------------------------------------
    # Find user
    # --------------------------------------

    db_user = crud.get_user_by_email(
        db,
        user.email
    )

    print("USER FOUND:", db_user is not None)

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    print("USER ID:", db_user.id)
    print("USERNAME:", db_user.username)

    # --------------------------------------
    # Verify password
    # --------------------------------------

    password_valid = verify_password(
        user.password,
        db_user.hashed_password
    )

    print("PASSWORD VALID:", password_valid)

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # --------------------------------------
    # Create JWT
    # --------------------------------------

    token = create_access_token(
        {
            "sub": db_user.email
        }
    )

    print("JWT CREATED")

    # --------------------------------------
    # Audit log
    # --------------------------------------

    crud.create_audit_log(
        db=db,
        user_id=db_user.id,
        action="LOGIN",
        module="Authentication",
        description=(
            f"User {db_user.username} "
            f"logged in successfully"
        )
    )

    print("LOGIN SUCCESS")
    print("================================\n")

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