from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from typing import List
from app.database import get_db
from app.models.collaboration import Collaboration, ProjectAssignment
from app.schemas.collaboration import CollaborationCreate, CollaborationOut, ProjectAssignmentCreate, ProjectAssignmentOut
from app.models.notification import Notification
router = APIRouter()

@router.post("/", response_model=CollaborationOut)
def create_collaboration(collab: CollaborationCreate, db: Session = Depends(get_db)):
    new_collab = Collaboration(**collab.dict())
    db.add(new_collab)
    db.commit()
    db.refresh(new_collab)

    # Auto-create notification
    notif = Notification(
        message=f"New collaboration started: {new_collab.project_name}",
        type="collaboration"
    )
    db.add(notif)
    db.commit()

    return new_collab


@router.get("/")
def list_collaborations(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("id", regex="^(id|project_name|institution_a|institution_b)$"),
    order: str = Query("desc", regex="^(asc|desc)$")
):
    query = db.query(Collaboration)

    sort_column = getattr(Collaboration, sort_by)
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    total = query.count()
    offset = (page - 1) * limit
    collaborations = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "collaborations": collaborations
    }


@router.get("/{collaboration_id}", response_model=CollaborationOut)
def get_collaboration(collaboration_id: int, db: Session = Depends(get_db)):
    collab = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
    if not collab:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    return collab


@router.delete("/{collaboration_id}")
def delete_collaboration(collaboration_id: int, db: Session = Depends(get_db)):
    collab = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
    if not collab:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    db.delete(collab)
    db.commit()
    return {"message": "Collaboration deleted successfully"}


@router.post("/assign", response_model=ProjectAssignmentOut)
def assign_researcher(assignment: ProjectAssignmentCreate, db: Session = Depends(get_db)):
    new_assignment = ProjectAssignment(**assignment.dict())
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment


@router.get("/assignments/{collaboration_id}", response_model=List[ProjectAssignmentOut])
def get_assignments(collaboration_id: int, db: Session = Depends(get_db)):
    return db.query(ProjectAssignment).filter(ProjectAssignment.collaboration_id == collaboration_id).all()