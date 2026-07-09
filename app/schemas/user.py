from datetime import date
from pydantic import BaseModel, EmailStr


# ----------------------------
# Base Schema
# ----------------------------
class UserBase(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    phone_number: str
    gender: str
    date_of_birth: date

    institution: str
    department: str
    designation: str

    specialization: str
    research_interests: str

    country: str
    state: str
    city: str


# ----------------------------
# Register Schema
# ----------------------------
class UserCreate(UserBase):
    password: str


# ----------------------------
# Login Schema
# ----------------------------
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ----------------------------
# Response Schema
# ----------------------------
class UserResponse(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True