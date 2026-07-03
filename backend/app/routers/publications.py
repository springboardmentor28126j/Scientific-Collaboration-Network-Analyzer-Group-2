from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.publication import Publication
from app.schemas.publication import PublicationCreate, PublicationUpdate, PublicationOut

router = APIRouter()

@router.post("/", response_model=PublicationOut)
def create_publication(pub: PublicationCreate, db: Session = Depends(get_db)):
    new_pub = Publication(**pub.dict())
    db.add(new_pub)
    db.commit()
    db.refresh(new_pub)
    return new_pub

@router.get("/", response_model=List[PublicationOut])
def list_publications(db: Session = Depends(get_db)):
    return db.query(Publication).all()

@router.get("/{publication_id}", response_model=PublicationOut)
def get_publication(publication_id: int, db: Session = Depends(get_db)):
    pub = db.query(Publication).filter(Publication.id == publication_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    return pub

@router.put("/{publication_id}", response_model=PublicationOut)
def update_publication(publication_id: int, pub_update: PublicationUpdate, db: Session = Depends(get_db)):
    pub = db.query(Publication).filter(Publication.id == publication_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    for field, value in pub_update.dict(exclude_unset=True).items():
        setattr(pub, field, value)
    db.commit()
    db.refresh(pub)
    return pub

@router.delete("/{publication_id}")
def delete_publication(publication_id: int, db: Session = Depends(get_db)):
    pub = db.query(Publication).filter(Publication.id == publication_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    db.delete(pub)
    db.commit()
    return {"message": "Publication deleted"}
