from schemas import PublicationCreate, PublicationUpdate, PublicationResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Publication, Researcher
from schemas import (
    PublicationCreate,
    PublicationUpdate,
    PublicationResponse
)

router = APIRouter(
    prefix="/publications",
    tags=["Publications"]
)


# =====================================================
# Get All Publications
# =====================================================
@router.get("/", response_model=list[PublicationResponse])
def get_publications(db: Session = Depends(get_db)):
    return db.query(Publication).all()


# =====================================================
# Get Publication By ID
# =====================================================
@router.get("/{publication_id}", response_model=PublicationResponse)
def get_publication(publication_id: int, db: Session = Depends(get_db)):

    publication = db.query(Publication).filter(
        Publication.publication_id == publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    return publication


# =====================================================
# Create Publication
# =====================================================
@router.post("/", response_model=PublicationResponse)
def add_publication(
    publication: PublicationCreate,
    db: Session = Depends(get_db)
):

    # Check whether researcher exists
    researcher = db.query(Researcher).filter(
        Researcher.researcher_id == publication.researcher_id
    ).first()

    if not researcher:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    new_publication = Publication(
        title=publication.title,
        abstract=publication.abstract,
        keywords=publication.keywords,
        author=publication.author,
        journal=publication.journal,
        year=publication.year,
        status=publication.status,
        pdf_file=publication.pdf_file,
        researcher_id=publication.researcher_id
    )

    db.add(new_publication)
    db.commit()
    db.refresh(new_publication)

    return new_publication


# =====================================================
# Update Publication
# =====================================================
@router.put("/{publication_id}", response_model=PublicationResponse)
def update_publication(
    publication_id: int,
    updated_data: PublicationUpdate,
    db: Session = Depends(get_db)
):

    publication = db.query(Publication).filter(
        Publication.publication_id == publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    # If researcher_id is updated, validate it
    if updated_data.researcher_id is not None:

        researcher = db.query(Researcher).filter(
            Researcher.researcher_id == updated_data.researcher_id
        ).first()

        if not researcher:
            raise HTTPException(
                status_code=404,
                detail="Researcher not found"
            )

    update_data = updated_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(publication, key, value)

    db.commit()
    db.refresh(publication)

    return publication


# =====================================================
# Delete Publication
# =====================================================
@router.delete("/{publication_id}")
def delete_publication(
    publication_id: int,
    db: Session = Depends(get_db)
):

    publication = db.query(Publication).filter(
        Publication.publication_id == publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    db.delete(publication)
    db.commit()

    return {
        "message": "Publication deleted successfully"
    }