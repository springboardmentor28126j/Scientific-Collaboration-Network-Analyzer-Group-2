from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
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

    # Audit log
    from app.models.audit_log import AuditLog
    log = AuditLog(user_id=new_pub.author_id, action="create_publication", details=f"Created publication: {new_pub.title}")
    db.add(log)
    db.commit()

    return new_pub


@router.get("/")
def list_publications(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("id", regex="^(id|title|type|status|year)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    status: Optional[PublicationStatus] = None,
    type: Optional[PublicationType] = None,
    author_id: Optional[int] = None
):
    query = db.query(Publication)

    if status:
        query = query.filter(Publication.status == status)
    if type:
        query = query.filter(Publication.type == type)
    if author_id:
        query = query.filter(Publication.author_id == author_id)

    sort_column = getattr(Publication, sort_by)
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    total = query.count()
    offset = (page - 1) * limit
    publications = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "publications": publications
    }


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

    # Audit log
    from app.models.audit_log import AuditLog
    log = AuditLog(user_id=pub.author_id, action="update_publication", details=f"Updated publication: {pub.title}")
    db.add(log)
    db.commit()

    return pub


@router.delete("/{publication_id}")
def delete_publication(publication_id: int, db: Session = Depends(get_db)):
    pub = db.query(Publication).filter(Publication.id == publication_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")

    pub_title = pub.title
    pub_author_id = pub.author_id

    db.delete(pub)
    db.commit()

    # Audit log
    from app.models.audit_log import AuditLog
    log = AuditLog(user_id=pub_author_id, action="delete_publication", details=f"Deleted publication: {pub_title}")
    db.add(log)
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