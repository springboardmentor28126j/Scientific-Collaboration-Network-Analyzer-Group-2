from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.schemas.activity_log import (
    ActivityLogCreate,
    ActivityLogResponse
)

from app import crud

router = APIRouter(
    prefix="/activity-logs",
    tags=["Activity Logs"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get(
    "/",
    response_model=list[ActivityLogResponse]
)
def get_all_logs(
    db: Session = Depends(get_db)
):

    return crud.get_all_activity_logs(db)


@router.get(
    "/project/{project_id}",
    response_model=list[ActivityLogResponse]
)
def get_project_logs(
    project_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_logs_by_project(
        db,
        project_id
    )


@router.get(
    "/researcher/{researcher_id}",
    response_model=list[ActivityLogResponse]
)
def get_researcher_logs(
    researcher_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_logs_by_researcher(
        db,
        researcher_id
    )


@router.post(
    "/",
    response_model=ActivityLogResponse
)
def create_log(
    log: ActivityLogCreate,
    db: Session = Depends(get_db)
):

    return crud.create_activity_log(
        db,
        log
    )


@router.delete(
    "/{log_id}"
)
def delete_log(
    log_id: int,
    db: Session = Depends(get_db)
):

    db_log = crud.get_activity_log_by_id(
        db,
        log_id
    )

    if not db_log:

        raise HTTPException(
            status_code=404,
            detail="Activity log not found"
        )

    return crud.delete_activity_log(
        db,
        db_log
    )