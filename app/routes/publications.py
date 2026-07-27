from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import shutil
import uuid

from app import crud, models, schemas
from app.database import get_db
from app.models import Publication, Researcher

router = APIRouter(
    prefix="/publications",
    tags=["Publications"]
)


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================
# CREATE PUBLICATION
# ============================

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_publication(
    publication: schemas.PublicationCreate,
    db: Session = Depends(get_db)
):

    # Check duplicate DOI
    if publication.doi:
        existing = db.query(models.Publication).filter(
            models.Publication.doi == publication.doi
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="A publication with this DOI already exists"
            )


    # Create publication
    new_publication = crud.create_publication(
        db,
        publication
    )


    # ==============================
    # CREATE COLLABORATIONS
    # ==============================

    researchers = db.query(Researcher).filter(
        Researcher.id.in_(publication.researcher_ids)
    ).all()


    if len(researchers) > 1:

        for i in range(len(researchers)):

            for j in range(i + 1, len(researchers)):

                collaboration = models.Collaboration(
                    researcher1_id=researchers[i].id,
                    researcher2_id=researchers[j].id,
                    publication_id=new_publication.id
                )

                db.add(collaboration)


        db.commit()


    return new_publication



# ============================
# GET ALL PUBLICATIONS
# ============================

@router.get("/")
def get_publications(
    db: Session = Depends(get_db)
):
    return crud.get_publications(db)



# ============================
# GET SINGLE PUBLICATION
# ============================

@router.get("/{publication_id}",
response_model=schemas.PublicationWithAuthors)
def get_publication(
    publication_id: int,
    db: Session = Depends(get_db)
):

    publication = db.query(Publication).filter(
        Publication.id == publication_id
    ).first()


    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )


    authors = []

    for link in publication.authors:

        authors.append(
            {
                "id": link.researcher.id,
                "full_name": link.researcher.full_name
            }
        )


    return {
        "id": publication.id,
        "title": publication.title,
        "authors": authors
    }



# ============================
# UPDATE PUBLICATION
# ============================

@router.put("/{publication_id}")
def update_publication(
    publication_id: int,
    updated_publication: schemas.PublicationCreate,
    db: Session = Depends(get_db)
):

    publication = crud.update_publication(
        db,
        publication_id,
        updated_publication
    )


    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )


    return publication



# ============================
# DELETE PUBLICATION
# ============================

@router.delete("/{publication_id}")
def delete_publication(
    publication_id: int,
    db: Session = Depends(get_db)
):

    publication = crud.delete_publication(
        db,
        publication_id
    )


    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )


    return {
        "message": "Publication deleted successfully",
        "publication_id": publication_id
    }



# ============================
# ASSIGN AUTHORS
# ============================

@router.post("/assign-authors")
def assign_authors(
    data: schemas.PublicationAuthorAssign,
    db: Session = Depends(get_db)
):

    publication = db.query(Publication).filter(
        Publication.id == data.publication_id
    ).first()


    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )


    researchers = db.query(Researcher).filter(
        Researcher.id.in_(data.researcher_ids)
    ).all()


    if not researchers:
        raise HTTPException(
            status_code=404,
            detail="Researchers not found"
        )


    for researcher in researchers:

        if researcher not in publication.authors:
            publication.authors.append(researcher)


    db.commit()


    return {
        "publication_id": publication.id,
        "authors": [
            {
                "id": r.id,
                "name": r.full_name
            }
            for r in publication.authors
        ]
    }



# ============================
# REMOVE AUTHORS
# ============================

@router.delete("/remove-author")
def remove_author(
    data: schemas.PublicationAuthorAssign,
    db: Session = Depends(get_db)
):

    for researcher_id in data.researcher_ids:

        link = db.query(models.PublicationAuthor).filter(
            models.PublicationAuthor.publication_id == data.publication_id,
            models.PublicationAuthor.researcher_id == researcher_id
        ).first()


        if link:
            db.delete(link)


    db.commit()


    return {
        "message": "Authors removed successfully"
    }



# ============================
# UPLOAD PDF
# ============================

@router.post("/upload/")
def upload_pdf(
    publication_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    publication = db.query(Publication).filter(
        Publication.id == publication_id
    ).first()


    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )


    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files allowed"
        )


    filename = f"{uuid.uuid4()}.pdf"

    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )


    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )


    publication.file_path = file_path


    db.commit()


    return {
        "message": "PDF uploaded successfully",
        "file_url": f"http://127.0.0.1:8000/files/{filename}"
    }



# ============================
# FILTER BY STATUS
# ============================

@router.get(
    "/status/{status}",
    response_model=list[schemas.PublicationResponse]
)
def get_publications_by_status(
    status: str,
    db: Session = Depends(get_db)
):

    return crud.get_publications_by_status(
        db,
        status
    )



# ============================
# FILTER BY INSTITUTION
# ============================

@router.get(
    "/institution/{institution_id}",
    response_model=list[schemas.PublicationResponse]
)
def get_publications_by_institution(
    institution_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_publications_by_institution(
        db,
        institution_id
    )