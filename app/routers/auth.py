from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, Researcher, Institution
from app.schemas import UserRegister, UserResponse
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter()


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Register API
@router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):

    # Check empty password
    if not user.password or user.password.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Password is required"
        )


    # Check if email already exists
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )


    # Allowed roles
    allowed_roles = [
        "researcher",
        "institution_admin",
        "reviewer"
    ]

    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Invalid role selected."
        )


    # ---------------- Institution Admin Validation ----------------

    institution = None

    if user.role == "institution_admin":

        if not user.institution_id:
            raise HTTPException(
                status_code=400,
                detail="Institution selection is required."
            )


        institution = db.query(Institution).filter(
            Institution.id == user.institution_id
        ).first()


        if not institution:
            raise HTTPException(
                status_code=400,
                detail="Institution not found. Please contact the System Admin."
            )


        if institution.user_id is not None:
            raise HTTPException(
                status_code=400,
                detail="This institution already has an Institution Admin."
            )


    # ---------------- Create User ----------------

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)



    # ---------------- Link Researcher ----------------

    if user.role == "researcher":

        existing_researcher = db.query(Researcher).filter(
            Researcher.email == user.email
        ).first()


        if existing_researcher:

            existing_researcher.user_id = new_user.id

            db.commit()



    # ---------------- Link Institution Admin ----------------

    if user.role == "institution_admin":

        institution.user_id = new_user.id

        db.commit()

        db.refresh(institution)



    return new_user
    
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()


    if not db_user:
        raise HTTPException(
            status_code=400,
            detail="Invalid email"
        )


    if not verify_password(
        form_data.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid password"
        )


    access_token = create_access_token(
        data={
            "sub": db_user.email,
            "user_id": db_user.id,
            "role": db_user.role
        }
    )


    researcher_id = None
    institution_name = None
    institution_id = None



    # -------- Researcher Login --------

    if db_user.role == "researcher":


        researcher = db.query(Researcher).filter(
            Researcher.user_id == db_user.id
        ).first()


        if researcher:

            researcher_id = researcher.id



    # -------- Institution Admin Login --------

    elif db_user.role == "institution_admin":


        institution = db.query(Institution).filter(
            Institution.user_id == db_user.id
        ).first()


        if institution:

            institution_name = institution.name

            institution_id = institution.id



    return {

        "access_token": access_token,

        "email": db_user.email,

        "full_name": db_user.full_name,

        "role": db_user.role,

        "user_id": db_user.id,

        "researcher_id": researcher_id,

        "institution": institution_name,

        "institution_id": institution_id

    }
@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db)
):

    return db.query(User).all()