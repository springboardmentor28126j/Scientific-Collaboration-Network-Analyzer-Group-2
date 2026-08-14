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


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # Check existing email
    existing_user = crud.get_user_by_email(
        db,
        user.email
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create user
    return crud.create_user(
        db,
        user
    )


# ============================================================
# GET CAPTCHA
# ============================================================

@router.get("/captcha")
def get_captcha():

    return generate_captcha()


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    print("\n======================================")
    print("LOGIN REQUEST")
    print("======================================")

    print("Email:", user.email)
    print("CAPTCHA ID:", user.captcha_id)
    print("CAPTCHA Answer:", user.captcha_answer)

    # --------------------------------------------------------
    # 1. CAPTCHA VALIDATION
    # --------------------------------------------------------

    captcha_valid = verify_captcha(
        user.captcha_id,
        user.captcha_answer
    )

    print("CAPTCHA VALID:", captcha_valid)

    if not captcha_valid:

        print("LOGIN FAILED: CAPTCHA")

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired CAPTCHA"
        )

    # --------------------------------------------------------
    # 2. FIND USER
    # --------------------------------------------------------

    db_user = crud.get_user_by_email(
        db,
        user.email
    )

    print(
        "USER FOUND:",
        db_user is not None
    )

    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # --------------------------------------------------------
    # 3. PASSWORD VALIDATION
    # --------------------------------------------------------

    password_valid = verify_password(
        user.password,
        db_user.hashed_password
    )

    print(
        "PASSWORD VALID:",
        password_valid
    )

    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # --------------------------------------------------------
    # 4. CREATE JWT
    # --------------------------------------------------------

    token = create_access_token(
        {
            "sub": db_user.email
        }
    )

    print("JWT CREATED")

    # --------------------------------------------------------
    # 5. AUDIT LOG
    # --------------------------------------------------------

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
    print("======================================\n")

    # --------------------------------------------------------
    # 6. RESPONSE
    # --------------------------------------------------------

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": db_user.username,
        "full_name": db_user.full_name,
        "role": db_user.role
    }


# ============================================================
# SWAGGER / OAUTH2 LOGIN
# ============================================================

@router.post("/token")
def get_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # Swagger uses username field.
    # In our application username = email.

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

    # Create token

    token = create_access_token(
        {
            "sub": db_user.email
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ============================================================
# CURRENT USER
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    email = payload.get("sub")

    if not email:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

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


# ============================================================
# UPDATE PROFILE
# ============================================================

@router.put(
    "/update-profile",
    response_model=UserResponse
)
def update_profile(
    updated_user: UserUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    email = payload.get("sub")

    if not email:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

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

    updated_profile = crud.update_user(
        db,
        db_user,
        updated_user
    )

    # Audit log

    crud.create_audit_log(
        db=db,
        user_id=db_user.id,
        action="PROFILE_UPDATED",
        module="User Profile",
        description=(
            f"User {db_user.username} "
            f"updated profile information"
        )
    )

    return updated_profile