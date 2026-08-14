from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


# ============================================================
# BASE USER SCHEMA
# ============================================================

class UserBase(BaseModel):

    full_name: str
    username: str
    email: EmailStr

    phone_number: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None

    institution: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None

    specialization: Optional[str] = None
    research_interests: Optional[str] = None

    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None

    website: Optional[str] = None
    established_year: Optional[str] = None
    institution_type: Optional[str] = None

    role: str = "Researcher"


# ============================================================
# REGISTER
# ============================================================

class UserCreate(UserBase):

    password: str


# ============================================================
# LOGIN
# ============================================================

class UserLogin(BaseModel):

    email: EmailStr
    password: str

    # CAPTCHA fields
    captcha_id: str
    captcha_answer: str


# ============================================================
# UPDATE PROFILE
# ============================================================

class UserUpdate(BaseModel):

    full_name: Optional[str] = None
    phone_number: Optional[str] = None

    institution: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None

    specialization: Optional[str] = None
    research_interests: Optional[str] = None

    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None

    website: Optional[str] = None


# ============================================================
# RESPONSE
# ============================================================

class UserResponse(UserBase):

    id: int

    class Config:
        from_attributes = True