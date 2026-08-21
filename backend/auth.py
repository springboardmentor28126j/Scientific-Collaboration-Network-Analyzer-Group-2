from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

users = []


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(user: RegisterRequest):

    for u in users:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    users.append(user.dict())

    return {
        "message": "User Registered Successfully"
    }


@router.post("/login")
def login(user: LoginRequest):

    for u in users:
        if u["email"] == user.email and u["password"] == user.password:
            return {
                "message": "Login Successful"
            }

    raise HTTPException(status_code=401, detail="Invalid Email or Password")