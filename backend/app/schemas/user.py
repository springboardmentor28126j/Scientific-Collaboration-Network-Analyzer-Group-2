from pydantic import BaseModel, EmailStr
from app.models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.RESEARCHER

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True
