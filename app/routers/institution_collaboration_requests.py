from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.schemas.institution_collaboration_request import (
    InstitutionCollaborationRequestCreate,
    InstitutionCollaborationRequestUpdate,
    InstitutionCollaborationRequestResponse
)
from app import crud

router = APIRouter(
    prefix="/institution-collaboration-requests",
    tags=["Institution Collaboration Requests"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=list[InstitutionCollaborationRequestResponse]
)
def get_all_requests(
    db: Session = Depends(get_db)
):
    return crud.get_all_institution_requests(db)


@router.get(
    "/sender/{institution_id}",
    response_model=list[InstitutionCollaborationRequestResponse]
)
def get_sender_requests(
    institution_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_requests_by_sender_institution(
        db,
        institution_id
    )


@router.get(
    "/receiver/{institution_id}",
    response_model=list[InstitutionCollaborationRequestResponse]
)
def get_receiver_requests(
    institution_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_requests_by_receiver_institution(
        db,
        institution_id
    )


@router.post(
    "/",
    response_model=InstitutionCollaborationRequestResponse
)
def create_request(
    request: InstitutionCollaborationRequestCreate,
    db: Session = Depends(get_db)
):
    return crud.create_institution_request(
        db,
        request
    )


@router.put(
    "/{request_id}",
    response_model=InstitutionCollaborationRequestResponse
)
def update_request(
    request_id: int,
    request: InstitutionCollaborationRequestUpdate,
    db: Session = Depends(get_db)
):

    db_request = crud.get_institution_request_by_id(
        db,
        request_id
    )

    if not db_request:
        raise HTTPException(
            status_code=404,
            detail="Institution collaboration request not found"
        )

    return crud.update_institution_request(
        db,
        db_request,
        request
    )


@router.delete("/{request_id}")
def delete_request(
    request_id: int,
    db: Session = Depends(get_db)
):

    db_request = crud.get_institution_request_by_id(
        db,
        request_id
    )

    if not db_request:
        raise HTTPException(
            status_code=404,
            detail="Institution collaboration request not found"
        )

    return crud.delete_institution_request(
        db,
        db_request
    )