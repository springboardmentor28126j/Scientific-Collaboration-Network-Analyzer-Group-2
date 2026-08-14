from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.routers.audit import create_activity_log
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


# =========================================================
# ADD RESEARCHER
# =========================================================

@router.post("/", response_model=schemas.ResearcherResponse)
def create_researcher(
    researcher: schemas.ResearcherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # ROLE CHECK
    # -----------------------------------------------------

    if current_user.role not in [
        "institution_admin",
        "system_admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to add researchers"
        )

    # -----------------------------------------------------
    # INSTITUTION ADMIN CAN ONLY ADD TO OWN INSTITUTION
    # -----------------------------------------------------

    if current_user.role == "institution_admin":

        if researcher.institution != current_user.institution:
            raise HTTPException(
                status_code=403,
                detail="You can only add researchers to your institution"
            )

    # -----------------------------------------------------
    # CHECK WHETHER USER ACCOUNT EXISTS
    # -----------------------------------------------------

    user = db.query(User).filter(
        User.email == researcher.email
    ).first()

    # -----------------------------------------------------
    # CHECK EXISTING RESEARCHER PROFILE
    # -----------------------------------------------------

    if user:

        existing_researcher = db.query(Researcher).filter(
            Researcher.user_id == user.id
        ).first()

        if existing_researcher:
            raise HTTPException(
                status_code=400,
                detail="Researcher profile already exists for this user"
            )

    # -----------------------------------------------------
    # ALSO CHECK BY EMAIL
    # -----------------------------------------------------

    existing_email = db.query(Researcher).filter(
        Researcher.email == researcher.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="A researcher with this email already exists"
        )

    # -----------------------------------------------------
    # CREATE RESEARCHER
    # -----------------------------------------------------

    new_researcher = Researcher(

        user_id=user.id if user else None,

        full_name=researcher.full_name,

        email=researcher.email,

        department=researcher.department,

        institution=researcher.institution,

        designation=researcher.designation,

        research_interests=researcher.research_interests,

        skills=researcher.skills,

        phone=researcher.phone
    )

    db.add(new_researcher)

    db.commit()

    db.refresh(new_researcher)
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        description=f"Created researcher '{new_researcher.full_name}'"
    )
    return new_researcher


# =========================================================
# CREATE RESEARCHER PROFILE
# =========================================================

@router.post(
    "/profile",
    response_model=schemas.ResearcherResponse
)
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


# =========================================================
# UPDATE MY PROFILE
# =========================================================

@router.put(
    "/profile",
    response_model=schemas.ResearcherResponse
)
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


# =========================================================
# GET ALL RESEARCHERS
# =========================================================

@router.get("/")
def get_all_researchers(
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "full_name",
    order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------------------

    if page < 1:
        page = 1

    if page_size < 1 or page_size > 100:
        page_size = 10

    if sort_by not in [
        "full_name",
        "email",
        "institution"
    ]:
        sort_by = "full_name"

    if order not in [
        "asc",
        "desc"
    ]:
        order = "asc"

    # -----------------------------------------------------
    # ROLE BASED QUERY
    # -----------------------------------------------------

    query = db.query(Researcher)

    # Institution Admin
    if current_user.role == "institution_admin":

        query = query.filter(
            Researcher.institution == current_user.institution
        )

    # System Admin
    elif current_user.role == "system_admin":

        # System admin sees everything
        pass

    # Researcher
    elif current_user.role == "researcher":

        query = query.filter(
            Researcher.user_id == current_user.id
        )

    else:

        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view researchers"
        )

    # -----------------------------------------------------
    # SORTING
    # -----------------------------------------------------

    if sort_by == "full_name":

        if order == "asc":
            query = query.order_by(
                Researcher.full_name.asc()
            )
        else:
            query = query.order_by(
                Researcher.full_name.desc()
            )

    elif sort_by == "email":

        if order == "asc":
            query = query.order_by(
                Researcher.email.asc()
            )
        else:
            query = query.order_by(
                Researcher.email.desc()
            )

    elif sort_by == "institution":

        if order == "asc":
            query = query.order_by(
                Researcher.institution.asc()
            )
        else:
            query = query.order_by(
                Researcher.institution.desc()
            )

    # -----------------------------------------------------
    # TOTAL RECORDS
    # -----------------------------------------------------

    total_records = query.count()

    # -----------------------------------------------------
    # TOTAL PAGES
    # -----------------------------------------------------

    total_pages = (
        (total_records + page_size - 1)
        // page_size
        if total_records > 0
        else 1
    )

    # -----------------------------------------------------
    # FIX PAGE
    # -----------------------------------------------------

    if page > total_pages:
        page = total_pages

    if page < 1:
        page = 1

    # -----------------------------------------------------
    # OFFSET
    # -----------------------------------------------------

    offset = (page - 1) * page_size

    # -----------------------------------------------------
    # GET PAGE
    # -----------------------------------------------------

    researchers = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    pagination = {

        "page": page,

        "page_size": page_size,

        "total_records": total_records,

        "total_pages": total_pages,

        "offset": offset
    }

    return {

        "data": researchers,

        "pagination": pagination
    }


# =========================================================
# GET MY PROFILE
# =========================================================

@router.get(
    "/profile/me",
    response_model=schemas.ResearcherResponse
)
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


# =========================================================
# GET RESEARCHER BY ID
# =========================================================

@router.get(
    "/{researcher_id}",
    response_model=schemas.ResearcherResponse
)
def get_researcher(
    researcher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    researcher = crud.get_researcher_by_id(
        db,
        researcher_id
    )

    if not researcher:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    # Institution admin can only view own institution
    if current_user.role == "institution_admin":

        if researcher.institution != current_user.institution:
            raise HTTPException(
                status_code=403,
                detail="You cannot view this researcher"
            )

    # Researcher can only view own profile
    elif current_user.role == "researcher":

        if researcher.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You cannot view this researcher"
            )

    return researcher


# =========================================================
# UPDATE RESEARCHER
# =========================================================

# =========================================================
# UPDATE RESEARCHER
# =========================================================

@router.put(
    "/{researcher_id}",
    response_model=schemas.ResearcherResponse
)
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

    existing = crud.get_researcher_by_id(
        db,
        researcher_id
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    # Institution Admin can only update own institution
    if current_user.role == "institution_admin":

        if existing.institution != current_user.institution:
            raise HTTPException(
                status_code=403,
                detail="You cannot update this researcher"
            )

        # Prevent moving researcher to another institution
        if researcher.institution != current_user.institution:
            raise HTTPException(
                status_code=403,
                detail="You cannot move a researcher to another institution"
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

    # Create audit log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        description=f"Updated researcher '{updated.full_name}'"
    )

    return updated


# =========================================================
# DELETE RESEARCHER
# =========================================================

@router.delete("/{researcher_id}")
def delete_researcher(
    researcher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Only System Admin
    if current_user.role != "system_admin":

        raise HTTPException(
            status_code=403,
            detail="Only System Admin can delete researchers"
        )

    # Get researcher before deleting
    researcher = crud.get_researcher_by_id(
        db,
        researcher_id
    )

    if not researcher:

        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    # Store name before deletion
    researcher_name = researcher.full_name

    deleted = crud.delete_researcher(
        db,
        researcher_id
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    # Create audit log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        description=f"Deleted researcher '{researcher_name}'"
    )

    return {
        "message": "Researcher deleted successfully"
    }
# =========================================================
# GET RESEARCHER BY USER ID
# =========================================================

@router.get(
    "/user/{user_id}",
    response_model=schemas.ResearcherResponse
)
def get_researcher_by_user_id(
    user_id: int,
    db: Session = Depends(get_db)
):

    researcher = (
        db.query(Researcher)
        .filter(
            Researcher.user_id == user_id
        )
        .first()
    )

    if not researcher:

        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    return researcher