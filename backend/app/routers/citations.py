from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from typing import Optional
from app.database import get_db
from app.models.citation import Citation
from app.schemas.citation import Citation as CitationSchema, CitationCreate, CitationUpdate

router = APIRouter(tags=["citations"])


@router.get("/")
def get_citations(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("id", regex="^(id|year|citation_style|title)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    citation_style: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None
):
    query = db.query(Citation)

    if citation_style:
        query = query.filter(Citation.citation_style == citation_style)
    if year:
        query = query.filter(Citation.year == year)
    if search:
        query = query.filter(
            Citation.title.ilike(f"%{search}%") |
            Citation.authors.ilike(f"%{search}%")
        )

    sort_column = getattr(Citation, sort_by)
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    total = query.count()
    offset = (page - 1) * limit
    citations = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "citations": citations
    }


@router.get("/{citation_id}")
def get_citation(citation_id: int, db: Session = Depends(get_db)):
    citation = db.query(Citation).filter(Citation.id == citation_id).first()
    if not citation:
        raise HTTPException(status_code=404, detail="Citation not found")
    return citation


@router.post("/")
def create_citation(citation: CitationCreate, db: Session = Depends(get_db)):
    db_citation = Citation(**citation.dict())
    db.add(db_citation)
    db.commit()
    db.refresh(db_citation)

    # Audit log
    from app.models.audit_log import AuditLog
    log = AuditLog(user_id=1, action="create_citation", details=f"Created citation: {db_citation.title or 'Untitled'}")
    db.add(log)
    db.commit()

    return db_citation


@router.put("/{citation_id}")
def update_citation(citation_id: int, citation: CitationUpdate, db: Session = Depends(get_db)):
    db_citation = db.query(Citation).filter(Citation.id == citation_id).first()
    if not db_citation:
        raise HTTPException(status_code=404, detail="Citation not found")

    update_data = citation.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_citation, field, value)

    db.commit()
    db.refresh(db_citation)

    # Audit log
    from app.models.audit_log import AuditLog
    log = AuditLog(user_id=1, action="update_citation", details=f"Updated citation: {db_citation.title or 'Untitled'}")
    db.add(log)
    db.commit()

    return db_citation


@router.delete("/{citation_id}")
def delete_citation(citation_id: int, db: Session = Depends(get_db)):
    db_citation = db.query(Citation).filter(Citation.id == citation_id).first()
    if not db_citation:
        raise HTTPException(status_code=404, detail="Citation not found")

    citation_title = db_citation.title or "Untitled"

    db.delete(db_citation)
    db.commit()

    # Audit log
    from app.models.audit_log import AuditLog
    log = AuditLog(user_id=1, action="delete_citation", details=f"Deleted citation: {citation_title}")
    db.add(log)
    db.commit()

    return {"message": "Citation deleted"}