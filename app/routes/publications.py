from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/publications",
    tags=["Publications"]
)


# ✅ CREATE PUBLICATION
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


# ✅ GET ALL PUBLICATIONS
@router.get("/")
def get_publications(db: Session = Depends(get_db)):
    return crud.get_publications(db)


@router.delete("/remove-author")
def remove_author(data: schemas.PublicationAuthorAssign, db: Session = Depends(get_db)):

    for researcher_id in data.researcher_ids:

        link = db.query(models.PublicationAuthor).filter(
            models.PublicationAuthor.publication_id == data.publication_id,
            models.PublicationAuthor.researcher_id == researcher_id
        ).first()

        if link:
            db.delete(link)

    db.commit()

    return {"message": "Authors removed successfully"}

@router.get("/{publication_id}", response_model=schemas.PublicationWithAuthors)
def get_publication(publication_id: int, db: Session = Depends(get_db)):

    publication = db.query(models.Publication).filter(
        models.Publication.id == publication_id
    ).first()

    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")

    authors = []
    for link in publication.authors:
        authors.append({
            "id": link.researcher.id,
            "full_name": link.researcher.full_name
        })

    return {
        "id": publication.id,
        "title": publication.title,
        "authors": authors
    }


# ✅ UPDATE PUBLICATION
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


# ✅ DELETE PUBLICATION
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


# ✅ ASSIGN AUTHORS (WITH DUPLICATE PREVENTION)
@router.post("/assign-authors")
def assign_authors(data: schemas.PublicationAuthorAssign, db: Session = Depends(get_db)):
    
    # ✅ Check if publication exists
    publication = db.query(models.Publication).filter(
        models.Publication.id == data.publication_id
    ).first()

    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")

    # ✅ Loop through researcher IDs
    for researcher_id in data.researcher_ids:

        researcher = db.query(models.Researcher).filter(
            models.Researcher.id == researcher_id
        ).first()

        if not researcher:
            raise HTTPException(
                status_code=404,
                detail=f"Researcher {researcher_id} not found"
            )

        # ✅ CHECK DUPLICATE
        existing = db.query(models.PublicationAuthor).filter(
            models.PublicationAuthor.publication_id == data.publication_id,
            models.PublicationAuthor.researcher_id == researcher_id
        ).first()

        if existing:
            continue  # skip if already exists

        # ✅ CREATE LINK
        link = models.PublicationAuthor(
            publication_id=data.publication_id,
            researcher_id=researcher_id
        )

        db.add(link)

    db.commit()

    return {"message": "Authors assigned successfully"}

