from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.schemas.collaboration_request import (
    CollaborationRequestCreate,
    CollaborationRequestUpdate,
    CollaborationRequestResponse
)
from app import crud

router = APIRouter(
    prefix="/collaboration-requests",
    tags=["Collaboration Requests"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=list[CollaborationRequestResponse]
)
def get_all_requests(
    db: Session = Depends(get_db)
):
    return crud.get_all_collaboration_requests(db)


@router.get(
    "/receiver/{receiver_id}",
    response_model=list[CollaborationRequestResponse]
)
def get_receiver_requests(
    receiver_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_requests_by_receiver(
        db,
        receiver_id
    )


@router.get(
    "/sender/{sender_id}",
    response_model=list[CollaborationRequestResponse]
)
def get_sender_requests(
    sender_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_requests_by_sender(
        db,
        sender_id
    )


@router.post(
    "/",
    response_model=CollaborationRequestResponse
)
def create_request(
    request: CollaborationRequestCreate,
    db: Session = Depends(get_db)
):
    return crud.create_collaboration_request(
        db,
        request
    )


@router.put(
    "/{request_id}",
    response_model=CollaborationRequestResponse
)
def update_request(
    request_id: int,
    request: CollaborationRequestUpdate,
    db: Session = Depends(get_db)
):

    db_request = crud.get_collaboration_request_by_id(
        db,
        request_id
    )

    if not db_request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    return crud.update_collaboration_request(
        db,
        db_request,
        request
    )


@router.delete("/{request_id}")
def delete_request(
    request_id: int,
    db: Session = Depends(get_db)
):

    db_request = crud.get_collaboration_request_by_id(
        db,
        request_id
    )

    if not db_request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    return crud.delete_collaboration_request(
        db,
        db_request
    )