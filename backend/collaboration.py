from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Collaboration, Researcher
from schemas import (
    CollaborationCreate,
    CollaborationResponse
)

router = APIRouter(
    prefix="/collaborations",
    tags=["Collaborations"]
)


# =====================================================
# Get All Collaborations
# =====================================================

@router.get("/", response_model=list[CollaborationResponse])
def get_collaborations(
    db: Session = Depends(get_db)
):
    return db.query(Collaboration).all()


# =====================================================
# Get Collaboration By ID
# =====================================================

@router.get(
    "/{collaboration_id}",
    response_model=CollaborationResponse
)
def get_collaboration(
    collaboration_id: int,
    db: Session = Depends(get_db)
):

    collaboration = db.query(Collaboration).filter(
        Collaboration.collaboration_id == collaboration_id
    ).first()

    if not collaboration:
        raise HTTPException(
            status_code=404,
            detail="Collaboration not found"
        )

    return collaboration


# =====================================================
# Create Collaboration
# =====================================================

@router.post(
    "/",
    response_model=CollaborationResponse
)
def add_collaboration(
    collaboration: CollaborationCreate,
    db: Session = Depends(get_db)
):

    # Check Researcher 1
    researcher1 = db.query(Researcher).filter(
        Researcher.researcher_id ==
        collaboration.researcher1_id
    ).first()

    if not researcher1:
        raise HTTPException(
            status_code=404,
            detail="Researcher 1 not found"
        )

    # Check Researcher 2
    researcher2 = db.query(Researcher).filter(
        Researcher.researcher_id ==
        collaboration.researcher2_id
    ).first()

    if not researcher2:
        raise HTTPException(
            status_code=404,
            detail="Researcher 2 not found"
        )

    # Prevent same researcher collaborating with themselves
    if (
        collaboration.researcher1_id ==
        collaboration.researcher2_id
    ):
        raise HTTPException(
            status_code=400,
            detail="A researcher cannot collaborate with themselves"
        )

    new_collaboration = Collaboration(
        researcher1_id=collaboration.researcher1_id,
        researcher2_id=collaboration.researcher2_id,
        project=collaboration.project,
        institution=collaboration.institution,
        collaboration_type=collaboration.collaboration_type,
        start_date=collaboration.start_date,
        status=collaboration.status
    )

    db.add(new_collaboration)
    db.commit()
    db.refresh(new_collaboration)

    return new_collaboration


# =====================================================
# Delete Collaboration
# =====================================================

@router.delete("/{collaboration_id}")
def delete_collaboration(
    collaboration_id: int,
    db: Session = Depends(get_db)
):

    collaboration = db.query(Collaboration).filter(
        Collaboration.collaboration_id == collaboration_id
    ).first()

    if not collaboration:
        raise HTTPException(
            status_code=404,
            detail="Collaboration not found"
        )

    db.delete(collaboration)
    db.commit()

    return {
        "message": "Collaboration deleted successfully"
    }