from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.collaboration import Collaboration, ProjectAssignment
from app.schemas.collaboration import CollaborationCreate, CollaborationOut, ProjectAssignmentCreate, ProjectAssignmentOut

router = APIRouter()


@router.post("/", response_model=CollaborationOut)
def create_collaboration(collab: CollaborationCreate, db: Session = Depends(get_db)):
    new_collab = Collaboration(**collab.dict())
    db.add(new_collab)
    db.commit()
    db.refresh(new_collab)
    return new_collab


@router.get("/", response_model=List[CollaborationOut])
def list_collaborations(db: Session = Depends(get_db)):
    return db.query(Collaboration).all()


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