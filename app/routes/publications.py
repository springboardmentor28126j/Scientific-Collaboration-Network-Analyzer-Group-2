from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/publications",
    tags=["Publications"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_publication(
    publication: schemas.PublicationCreate,
    db: Session = Depends(get_db)
):
    if publication.doi:
        existing_publication = (
            db.query(models.Publication)
            .filter(models.Publication.doi == publication.doi)
            .first()
        )

        if existing_publication:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A publication with this DOI already exists"
            )

    return crud.create_publication(db, publication)


@router.get("/")
def get_publications(db: Session = Depends(get_db)):
    return crud.get_publications(db)

@router.get("/{publication_id}")
def get_publication(publication_id: int, db: Session = Depends(get_db)):
    publication = crud.get_publication_by_id(db, publication_id)

    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publication not found"
        )

    return publication

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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publication not found"
        )

    return publication

@router.delete("/{publication_id}")
def delete_publication(publication_id: int, db: Session = Depends(get_db)):
    publication = crud.delete_publication(db, publication_id)

    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publication not found"
        )

    return {
        "message": "Publication deleted successfully",
        "publication_id": publication_id
    }