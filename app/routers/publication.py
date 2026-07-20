from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app import schemas, crud, models
from app.models import User
from app.database import SessionLocal
from app.oauth2 import get_current_user

import os
from pathlib import Path
from uuid import uuid4

router = APIRouter(
    prefix="/publications",
    tags=["Publications"]
)
UPLOAD_FOLDER = "uploads/publications"

Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.PublicationResponse)
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

    filename = None

    if file:
        filename = f"{uuid4()}_{file.filename}"

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())


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


    return crud.create_publication(db, publication)

@router.get("/", response_model=list[schemas.PublicationResponse])
def get_all_publications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    publications = (
        db.query(models.Publication)
        .join(models.Researcher)
        .all()
    )

    for pub in publications:
        pub.researcher_name = pub.researcher.full_name

    return publications

@router.get("/user/{user_id}", response_model=list[schemas.PublicationResponse])
def get_user_publications(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    publications = (
    db.query(models.Publication)
    .join(models.Researcher)
    .filter(models.Researcher.user_id == user_id)
    .all()
)

    print("USER ID:", user_id)
    print("PUBLICATIONS FOUND:", publications)

    return publications
@router.get("/{publication_id}", response_model=schemas.PublicationResponse)
def get_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    publication = crud.get_publication_by_id(db, publication_id)

    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")

    return publication


@router.put("/{publication_id}", response_model=schemas.PublicationResponse)
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

    existing = crud.get_publication_by_id(db, publication_id)

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )


    # Keep old PDF if no new file is uploaded
    filename = existing.publication_file


    # If new PDF uploaded, replace with new file
    if file:

        filename = f"{uuid4()}_{file.filename}"

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())


    publication_data = schemas.PublicationUpdate(

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


    return updated


@router.delete("/{publication_id}")
def delete_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = crud.delete_publication(db, publication_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Publication not found")

    return {"message": "Publication deleted successfully"}