from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from database import get_db

router = APIRouter(prefix="/citations", tags=["Citations"])


# Add Citation
@router.post("/")
def add_citation(
    publication_id: int,
    cited_publication_id: int,
    doi: str = None,
    db: Session = Depends(get_db)
):
    publication = db.query(models.Publication).filter(
        models.Publication.publication_id == publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    cited_publication = db.query(models.Publication).filter(
        models.Publication.publication_id == cited_publication_id
    ).first()

    if not cited_publication:
        raise HTTPException(
            status_code=404,
            detail="Cited publication not found"
        )

    new_citation = models.Citation(
        publication_id=publication_id,
        cited_publication_id=cited_publication_id,
        doi=doi
    )

    db.add(new_citation)
    db.commit()
    db.refresh(new_citation)

    return new_citation


# Get All Citations
@router.get("/")
def get_citations(db: Session = Depends(get_db)):
    return db.query(models.Citation).all()


# Delete Citation
@router.delete("/{citation_id}")
def delete_citation(
    citation_id: int,
    db: Session = Depends(get_db)
):
    citation = db.query(models.Citation).filter(
        models.Citation.citation_id == citation_id
    ).first()

    if not citation:
        raise HTTPException(
            status_code=404,
            detail="Citation not found"
        )

    db.delete(citation)
    db.commit()

    return {"message": "Citation deleted successfully"}