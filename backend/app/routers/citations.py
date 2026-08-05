from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.citation import Citation
from app.models.publication import Publication
from app.schemas.citation import CitationCreate, CitationOut

router = APIRouter()


@router.post("/", response_model=CitationOut)
def create_citation(citation: CitationCreate, db: Session = Depends(get_db)):
    new_citation = Citation(**citation.dict())
    db.add(new_citation)
    db.commit()
    db.refresh(new_citation)
    return new_citation


@router.get("/", response_model=List[CitationOut])
def list_citations(db: Session = Depends(get_db)):
    return db.query(Citation).all()


@router.get("/publication/{publication_id}")
def get_citations_for_publication(publication_id: int, db: Session = Depends(get_db)):
    citing = db.query(Citation).filter(Citation.cited_publication_id == publication_id).all()

    result = []
    for c in citing:
        pub = db.query(Publication).filter(Publication.id == c.citing_publication_id).first()
        if pub:
            result.append({"citation_id": c.id, "citing_publication_title": pub.title, "citing_publication_id": pub.id})

    return {"cited_by_count": len(result), "citations": result}


@router.delete("/{citation_id}")
def delete_citation(citation_id: int, db: Session = Depends(get_db)):
    citation = db.query(Citation).filter(Citation.id == citation_id).first()
    if not citation:
        raise HTTPException(status_code=404, detail="Citation not found")
    db.delete(citation)
    db.commit()
    return {"message": "Citation deleted successfully"}