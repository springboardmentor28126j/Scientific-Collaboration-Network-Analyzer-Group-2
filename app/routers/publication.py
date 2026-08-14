from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app import schemas, crud, models
from app.models import User
from app.database import SessionLocal
from app.oauth2 import get_current_user
from app.ai_recommendation import get_recommendations
import os
from pathlib import Path
from uuid import uuid4


router = APIRouter(
    prefix="/publications",
    tags=["Publications"]
)


UPLOAD_FOLDER = "uploads/publications"

Path(UPLOAD_FOLDER).mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# DATABASE
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# =========================================================
# CREATE PUBLICATION
# =========================================================

@router.post(
    "/",
    response_model=schemas.PublicationResponse
)
def create_publication(

    researcher_id: int = Form(...),

    title: str = Form(...),

    publication_type: str = Form(...),

    journal_name: str | None = Form(None),

    conference_name: str | None = Form(None),

    publication_year: int = Form(...),

    doi: str | None = Form(None),

    status: str = Form(...),

    file: UploadFile | None = File(None),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    # =====================================================
    # FILE UPLOAD
    # =====================================================

    filename = None

    if file:

        filename = f"{uuid4()}_{file.filename}"

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(file_path, "wb") as buffer:

            buffer.write(
                file.file.read()
            )

    # =====================================================
    # CREATE PUBLICATION DATA
    # =====================================================

    publication = schemas.PublicationCreate(

        researcher_id=researcher_id,

        title=title,

        publication_type=publication_type,

        journal_name=journal_name,

        conference_name=conference_name,

        publication_year=publication_year,

        doi=doi,

        status=status,

        publication_file=filename

    )

    # =====================================================
    # SAVE PUBLICATION
    # =====================================================

    new_publication = crud.create_publication(
        db,
        publication
    )

    # =====================================================
    # CREATE AUDIT LOG
    # =====================================================

    crud.create_activity(

        db=db,

        user_id=current_user.id,

        action="CREATE",

        description=f"Created publication '{new_publication.title}'"

    )

    return new_publication


# =========================================================
# GET ALL PUBLICATIONS
# =========================================================

@router.get("/")
def get_all_publications(

    page: int = Query(
        1,
        ge=1
    ),

    # IMPORTANT:
    # Flask requests 1000 records so that it can perform
    # role filtering and pagination locally.
    page_size: int = Query(
        10,
        ge=1,
        le=1000
    ),

    sort_by: str = Query(
        "year"
    ),

    order: str = Query(
        "desc"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    # =====================================================
    # GET PUBLICATIONS
    # =====================================================

    publications, pagination = crud.get_all_publications(

        db,

        page,

        page_size,

        sort_by,

        order

    )

    # =====================================================
    # ADD RESEARCHER NAME
    # =====================================================

    for pub in publications:

        researcher = (
            db.query(models.Researcher)
            .filter(
                models.Researcher.id
                == pub.researcher_id
            )
            .first()
        )

        if researcher:

            pub.researcher_name = (
                researcher.full_name
            )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        "data": publications,

        "pagination": pagination

    }


# =========================================================
# GET PUBLICATIONS OF A USER
# =========================================================

@router.get(
    "/user/{user_id}",
    response_model=list[schemas.PublicationResponse]
)
def get_user_publications(

    user_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    publications = (

        db.query(models.Publication)

        .join(models.Researcher)

        .filter(
            models.Researcher.user_id
            == user_id
        )

        .all()

    )

    print(
        "USER ID:",
        user_id
    )

    print(
        "PUBLICATIONS FOUND:",
        publications
    )

    return publications

# =========================================================
# AI RESEARCH PAPER RECOMMENDATION
# =========================================================

@router.get("/recommend")
def recommend_publications(

    q: str = Query(
        ...,
        min_length=2
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    publications = (

        db.query(models.Publication)

        .filter(
            models.Publication.title.isnot(None)
        )

        .all()

    )

    recommendations = get_recommendations(
        q,
        publications
    )

    # =====================================================
    # ADD RESEARCHER NAME
    # =====================================================

    for recommendation in recommendations:

        researcher = (

            db.query(models.Researcher)

            .filter(

                models.Researcher.id
                == recommendation["researcher_id"]

            )

            .first()

        )

        if researcher:

            recommendation["researcher_name"] = (
                researcher.full_name
            )

        else:

            recommendation["researcher_name"] = (
                "Unknown"
            )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        "query": q,

        "recommendations": recommendations

    }
# =========================================================
# GET SINGLE PUBLICATION
# =========================================================

@router.get(
    "/{publication_id}",
    response_model=schemas.PublicationResponse
)
def get_publication(

    publication_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    publication = crud.get_publication_by_id(
        db,
        publication_id
    )

    if not publication:

        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    return publication

# =========================================================
# UPDATE PUBLICATION
# =========================================================

@router.put(
    "/{publication_id}",
    response_model=schemas.PublicationResponse
)
def update_publication(

    publication_id: int,

    researcher_id: int = Form(...),

    title: str = Form(...),

    publication_type: str = Form(...),

    journal_name: str | None = Form(None),

    conference_name: str | None = Form(None),

    publication_year: int = Form(...),

    doi: str | None = Form(None),

    status: str = Form(...),

    file: UploadFile | None = File(None),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    # =====================================================
    # GET EXISTING PUBLICATION
    # =====================================================

    existing = crud.get_publication_by_id(
        db,
        publication_id
    )

    if not existing:

        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    # =====================================================
    # STATUS RULES
    # =====================================================

    if existing.status in [
        "Published",
        "Rejected",
        "Archived"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Publication cannot be edited "
                f"because its status is "
                f"'{existing.status}'."
            )
        )

    # =====================================================
    # UNDER REVIEW
    # =====================================================

    if existing.status == "Under Review":

        final_status = "Under Review"

    # =====================================================
    # SUBMITTED
    # =====================================================

    elif existing.status == "Submitted":

        final_status = "Submitted"

    # =====================================================
    # DRAFT
    # =====================================================

    elif existing.status == "Draft":

        if status not in [
            "Draft",
            "Submitted"
        ]:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Draft publications can only "
                    "remain Draft or be submitted."
                )
            )

        final_status = status

    # =====================================================
    # OTHER
    # =====================================================

    else:

        final_status = existing.status

    # =====================================================
    # KEEP OLD FILE
    # =====================================================

    filename = existing.publication_file

    # =====================================================
    # NEW FILE
    # =====================================================

    if file:

        filename = (
            f"{uuid4()}_{file.filename}"
        )

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(
            file_path,
            "wb"
        ) as buffer:

            buffer.write(
                file.file.read()
            )

    # =====================================================
    # UPDATE DATA
    # =====================================================

    publication_data = schemas.PublicationUpdate(

        researcher_id=researcher_id,

        title=title,

        publication_type=publication_type,

        journal_name=journal_name,

        conference_name=conference_name,

        publication_year=publication_year,

        doi=doi,

        status=final_status,

        publication_file=filename

    )

    # =====================================================
    # UPDATE
    # =====================================================

    updated = crud.update_publication(

        db,

        publication_id,

        publication_data

    )

    if not updated:

        raise HTTPException(

            status_code=404,

            detail="Publication not found"

        )

    # =====================================================
    # CREATE AUDIT LOG
    # =====================================================

    crud.create_activity(

        db=db,

        user_id=current_user.id,

        action="UPDATE",

        description=f"Updated publication '{updated.title}'"

    )

    return updated


# =========================================================
# DELETE PUBLICATION
# =========================================================

@router.delete(
    "/{publication_id}"
)
def delete_publication(

    publication_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    # =====================================================
    # GET PUBLICATION BEFORE DELETE
    # =====================================================

    existing = crud.get_publication_by_id(
        db,
        publication_id
    )

    if not existing:

        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    publication_title = existing.title

    # =====================================================
    # DELETE PUBLICATION
    # =====================================================

    deleted = crud.delete_publication(

        db,

        publication_id

    )

    if not deleted:

        raise HTTPException(

            status_code=404,

            detail="Publication not found"

        )

    # =====================================================
    # CREATE AUDIT LOG
    # =====================================================

    crud.create_activity(

        db=db,

        user_id=current_user.id,

        action="DELETE",

        description=f"Deleted publication '{publication_title}'"

    )

    return {

        "message":
        "Publication deleted successfully"

    }
