from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import schemas, crud
from app.models import User, Researcher
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/researchers",
    tags=["Researchers"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.ResearcherResponse)
def create_researcher(
    researcher: schemas.ResearcherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role not in [
        "institution_admin",
        "system_admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to add researchers"
        )


    return crud.create_researcher(
        db,
        researcher,
        current_user.id
    )

@router.post("/profile", response_model=schemas.ResearcherResponse)
def create_researcher_profile(
    profile: schemas.ResearcherProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "researcher":

        raise HTTPException(
            status_code=403,
            detail="Only researchers can create their profile"
        )


    existing_profile = db.query(Researcher).filter(
        Researcher.user_id == current_user.id
    ).first()


    if existing_profile:

        raise HTTPException(
            status_code=400,
            detail="Researcher profile already exists"
        )


    researcher = Researcher(

        user_id=current_user.id,

        full_name=current_user.full_name,

        email=current_user.email,

        institution=profile.institution,

        department=profile.department,

        designation=profile.designation,

        research_interests=profile.research_interests,

        skills=profile.skills,

        phone=profile.phone
    )


    db.add(researcher)

    db.commit()

    db.refresh(researcher)


    return researcher

@router.put("/profile", response_model=schemas.ResearcherResponse)
def update_profile(
    profile: schemas.ResearcherProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    researcher = db.query(Researcher).filter(
        Researcher.user_id == current_user.id
    ).first()

    if not researcher:
        raise HTTPException(
            status_code=404,
            detail="Profile not found."
        )

    researcher.institution = profile.institution
    researcher.department = profile.department
    researcher.designation = profile.designation
    researcher.research_interests = profile.research_interests
    researcher.skills = profile.skills
    researcher.phone = profile.phone

    db.commit()
    db.refresh(researcher)

    return researcher

@router.get("/", response_model=list[schemas.ResearcherResponse])
def get_all_researchers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_all_researchers(db)

@router.get("/profile/me", response_model=schemas.ResearcherResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    researcher = db.query(Researcher).filter(
        Researcher.user_id == current_user.id
    ).first()


    if not researcher:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )


    return researcher

@router.get("/{researcher_id}", response_model=schemas.ResearcherResponse)
def get_researcher(
    researcher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    researcher = crud.get_researcher_by_id(db, researcher_id)

    if not researcher:
        raise HTTPException(status_code=404, detail="Researcher not found")

    return researcher


@router.put("/{researcher_id}", response_model=schemas.ResearcherResponse)
def update_researcher(
    researcher_id: int,
    researcher: schemas.ResearcherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role not in [
        "institution_admin",
        "system_admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="You cannot update researchers"
        )


    updated = crud.update_researcher(
        db,
        researcher_id,
        researcher
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    return updated


@router.delete("/{researcher_id}")
def delete_researcher(
    researcher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Only System Admin can delete researchers
    if current_user.role != "system_admin":
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can delete researchers"
        )


    deleted = crud.delete_researcher(
        db,
        researcher_id
    )


    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )


    return {
        "message": "Researcher deleted successfully"
    }
@router.get("/user/{user_id}", response_model=schemas.ResearcherResponse)
def get_researcher_by_user_id(
    user_id: int,
    db: Session = Depends(get_db)
):

    researcher = (
        db.query(Researcher)
        .filter(Researcher.user_id == user_id)
        .first()
    )

    if not researcher:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    return researcher