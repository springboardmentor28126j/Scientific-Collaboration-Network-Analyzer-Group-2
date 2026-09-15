from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from database import get_db
from models import User


router = APIRouter()


# =====================================================
# JWT Configuration
# =====================================================

SECRET_KEY = "scientific-collaboration-network-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =====================================================
# Bearer Authentication
# =====================================================

security = HTTPBearer()


# =====================================================
# Request Models
# =====================================================

class RegisterRequest(BaseModel):
    username: str
    email: str
    institution: str = ""
    department: str = ""
    country: str = ""
    role: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# =====================================================
# Allowed Roles
# =====================================================

ALLOWED_ROLES = [
    "Researcher",
    "Institution Admin",
    "Reviewer",
    "System Admin"
]


# =====================================================
# Password Functions
# =====================================================

def hash_password(password: str) -> str:

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(
    password: str,
    hashed_password: str
) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def is_hashed_password(password: str) -> bool:

    return password.startswith(
        ("$2a$", "$2b$", "$2y$")
    )


# =====================================================
# Create JWT Token
# =====================================================

def create_access_token(
    user_id: int,
    role: str
):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# =====================================================
# Register
# =====================================================

@router.post("/register")
def register(
    user: RegisterRequest,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    if user.role not in ALLOWED_ROLES:

        raise HTTPException(
            status_code=400,
            detail="Invalid role selected"
        )

    hashed_password = hash_password(
        user.password
    )

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User Registered Successfully",
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }


# =====================================================
# Login
# =====================================================

@router.post("/login")
def login(
    user: LoginRequest,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    # Check hashed password
    if is_hashed_password(existing_user.password):

        password_valid = verify_password(
            user.password,
            existing_user.password
        )

    # Support old plaintext passwords
    else:

        password_valid = (
            existing_user.password == user.password
        )

        # Convert old password to bcrypt
        if password_valid:

            existing_user.password = hash_password(
                user.password
            )

            db.commit()
            db.refresh(existing_user)

    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    access_token = create_access_token(
        existing_user.id,
        existing_user.role
    )

    return {
        "message": "Login Successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": existing_user.id,
        "username": existing_user.username,
        "email": existing_user.email,
        "role": existing_user.role
    }


# =====================================================
# Get Current Logged-in User
# =====================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid or expired authentication token"
    )

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:

            raise credentials_exception

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Authentication token has expired"
        )

    except jwt.InvalidTokenError:

        raise credentials_exception

    current_user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    if not current_user:

        raise credentials_exception

    return current_user


# =====================================================
# Role Authorization
# =====================================================

def require_roles(*allowed_roles):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource"
            )

        return current_user

    return role_checker