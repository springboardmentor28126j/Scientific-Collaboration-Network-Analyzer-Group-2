from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from app.database import get_db
from app.models.publication import Publication, PublicationStatus, PublicationType
from app.schemas.publication import PublicationCreate, PublicationUpdate, PublicationOut

router = APIRouter()

UPLOAD_DIR = "uploads"


@router.post("/", response_model=PublicationOut)
def create_publication(pub: PublicationCreate, db: Session = Depends(get_db)):
    new_pub = Publication(**pub.dict())
    db.add(new_pub)
    db.commit()
    db.refresh(new_pub)

    from app.models.notification import Notification
    notif = Notification(message=f"New publication added: {new_pub.title}", type="publication")
    db.add(notif)
    db.commit()

    return new_pub


@router.get("/", response_model=List[PublicationOut])
def list_publications(
    status: Optional[PublicationStatus] = None,
    type: Optional[PublicationType] = None,
    author_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Publication)

    if status:
        query = query.filter(Publication.status == status)
    if type:
        query = query.filter(Publication.type == type)
    if author_id:
        query = query.filter(Publication.author_id == author_id)

    return query.all()


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
    return {"message": "Publication deleted successfully"}


@router.post("/{publication_id}/upload")
def upload_publication_file(publication_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    pub = db.query(Publication).filter(Publication.id == publication_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{publication_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pub.file_path = file_path
    db.commit()
    db.refresh(pub)

    return {"message": "File uploaded successfully", "file_path": file_path}