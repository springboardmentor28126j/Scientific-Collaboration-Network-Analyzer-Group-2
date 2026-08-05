from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import User
from app.oauth2 import get_current_user
from ..database import get_db
from .. import schemas, crud, models


router = APIRouter(
    prefix="/references",
    tags=["References"]
)


# ==========================
# Create Reference
# ==========================

@router.post(
    "/",
    response_model=schemas.ReferenceResponse
)
def create_reference(
    reference: schemas.ReferenceCreate,
    db: Session = Depends(get_db)
):

    try:

        return crud.create_reference(
            db,
            reference
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )



# ==========================
# Get References by Publication
# ==========================

@router.get(
    "/publication/{publication_id}",
    response_model=list[schemas.ReferenceResponse]
)
def get_references(
    publication_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_references_by_publication(
        db,
        publication_id
    )


@router.get("/")
def get_all_references(
    db: Session = Depends(get_db)
):

    references = db.query(models.Reference).all()

    result = []

    for reference in references:

        publication = db.query(models.Publication).filter(
            models.Publication.id == reference.publication_id
        ).first()

        result.append({

            "id": reference.id,

            "publication_id": reference.publication_id,

            "publication_title": publication.title if publication else "Unknown",

            "reference_title": reference.reference_title,

            "author": reference.author,

            "publication_year": reference.publication_year,

            "doi": reference.doi,

            "created_at": reference.created_at

        })

    return result
    
# ==========================
# Get Single Reference
# ==========================

@router.get(
    "/{reference_id}",
    response_model=schemas.ReferenceResponse
)
def get_reference(
    reference_id: int,
    db: Session = Depends(get_db)
):

    reference = crud.get_reference_by_id(
        db,
        reference_id
    )


    if not reference:

        raise HTTPException(
            status_code=404,
            detail="Reference not found"
        )


    return reference



# ==========================
# Delete Reference
# ==========================

@router.delete("/{reference_id}")
def delete_reference(
    reference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    reference = db.query(models.Reference).filter(
        models.Reference.id == reference_id
    ).first()


    if not reference:
        raise HTTPException(
            status_code=404,
            detail="Reference not found"
        )


    # System Admin can delete any reference
    if current_user.role == "system_admin":
        pass


    # Researcher can delete only their own publication references
    elif current_user.role == "researcher":

        publication = db.query(models.Publication).filter(
            models.Publication.id == reference.publication_id
        ).first()


        if not publication:
            raise HTTPException(
                status_code=404,
                detail="Publication not found"
            )


        if publication.researcher_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can delete only references from your own publications"
            )


    else:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )


    db.delete(reference)
    db.commit()


    return {
        "message": "Reference deleted successfully"
    }