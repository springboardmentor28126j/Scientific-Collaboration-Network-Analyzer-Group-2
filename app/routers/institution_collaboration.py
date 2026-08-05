from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, crud


router = APIRouter(
    prefix="/institution-collaborations",
    tags=["Institution Collaborations"]
)


# ==========================
# Create Institution Collaboration
# ==========================

@router.post(
    "/",
    response_model=schemas.InstitutionCollaborationResponse
)
def create_collaboration(
    collaboration: schemas.InstitutionCollaborationCreate,
    db: Session = Depends(get_db)
):

    return crud.create_institution_collaboration(
        db,
        collaboration
    )



# ==========================
# Get All Collaborations
# ==========================

@router.get(
    "/",
    response_model=list[schemas.InstitutionCollaborationResponse]
)
def get_collaborations(
    db: Session = Depends(get_db)
):

    return crud.get_institution_collaborations(
        db
    )



# ==========================
# Delete Collaboration
# ==========================

@router.delete("/{collaboration_id}")
def delete_collaboration(
    collaboration_id: int,
    db: Session = Depends(get_db)
):

    collaboration = crud.delete_institution_collaboration(
        db,
        collaboration_id
    )


    if not collaboration:

        raise HTTPException(
            status_code=404,
            detail="Collaboration not found"
        )


    return {
        "message": "Institution collaboration removed"
    }