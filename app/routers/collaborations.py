from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app import crud
from app.schemas.collaboration import (
    CollaborationCreate,
    CollaborationResponse,
)

router = APIRouter(
    prefix="/collaborations",
    tags=["Collaborations"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CollaborationResponse)
def add_collaboration(
    collaboration: CollaborationCreate,
    db: Session = Depends(get_db)
):
    return crud.create_collaboration(db, collaboration)
from fastapi import HTTPException
import traceback

@router.get("/", response_model=list[CollaborationResponse])
def get_collaborations(db: Session = Depends(get_db)):
    try:
        return crud.get_all_collaborations(db)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    return crud.get_my_collaborations(db, researcher_id)


@router.put("/{collaboration_id}/accept",
            response_model=CollaborationResponse)
def accept_request(
    collaboration_id: int,
    db: Session = Depends(get_db)
):

    collaboration = crud.get_collaboration_by_id(
        db,
        collaboration_id
    )

    if not collaboration:
        raise HTTPException(
            status_code=404,
            detail="Collaboration not found"
        )

    return crud.accept_collaboration(
        db,
        collaboration
    )


@router.put("/{collaboration_id}/reject",
            response_model=CollaborationResponse)
def reject_request(
    collaboration_id: int,
    db: Session = Depends(get_db)
):

    collaboration = crud.get_collaboration_by_id(
        db,
        collaboration_id
    )

    if not collaboration:
        raise HTTPException(
            status_code=404,
            detail="Collaboration not found"
        )

    return crud.reject_collaboration(
        db,
        collaboration
    )
from fastapi import HTTPException
import traceback

@router.get("/", response_model=list[CollaborationResponse])
def get_collaborations(db: Session = Depends(get_db)):
    try:
        return crud.get_all_collaborations(db)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))