from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import traceback

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

    try:

        data = crud.get_all_institution_collaboration_requests(db)

        print("GET RESPONSE =", data)

        return data

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@router.get(
    "/accepted",
    response_model=list[InstitutionCollaborationRequestResponse]
)
def get_accepted_requests(
    db: Session = Depends(get_db)
):

    return crud.get_accepted_institution_collaboration_requests(db)


@router.post(
    "/",
    response_model=InstitutionCollaborationRequestResponse
)
def create_request(
    request: InstitutionCollaborationRequestCreate,
    db: Session = Depends(get_db)
):

    try:

        print("REQUEST BODY =", request.model_dump())

        data = crud.create_institution_collaboration_request(
            db,
            request
        )

        print("CREATED =", data)

        return data

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
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


    try:

        db_request = crud.get_institution_collaboration_request_by_id(
            db,
            request_id
        )

        if not db_request:

            raise HTTPException(
                status_code=404,
                detail="Institution Collaboration Request Not Found"
            )

        return crud.update_institution_collaboration_request(
            db,
            db_request,
            request
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )