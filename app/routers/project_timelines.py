from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.schemas.project_timeline import (
    ProjectTimelineCreate,
    ProjectTimelineUpdate,
    ProjectTimelineResponse
)
from app import crud

router = APIRouter(
    prefix="/project-timelines",
    tags=["Project Timelines"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=list[ProjectTimelineResponse]
)
def get_all_timelines(
    db: Session = Depends(get_db)
):
    return crud.get_all_project_timelines(db)


@router.get(
    "/project/{project_id}",
    response_model=list[ProjectTimelineResponse]
)
def get_project_timelines(
    project_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_timelines_by_project(
        db,
        project_id
    )


@router.post(
    "/",
    response_model=ProjectTimelineResponse
)
def create_timeline(
    timeline: ProjectTimelineCreate,
    db: Session = Depends(get_db)
):
    return crud.create_project_timeline(
        db,
        timeline
    )


@router.put(
    "/{timeline_id}",
    response_model=ProjectTimelineResponse
)
def update_timeline(
    timeline_id: int,
    timeline: ProjectTimelineUpdate,
    db: Session = Depends(get_db)
):

    db_timeline = crud.get_project_timeline_by_id(
        db,
        timeline_id
    )

    if not db_timeline:
        raise HTTPException(
            status_code=404,
            detail="Timeline event not found"
        )

    return crud.update_project_timeline(
        db,
        db_timeline,
        timeline
    )


@router.delete("/{timeline_id}")
def delete_timeline(
    timeline_id: int,
    db: Session = Depends(get_db)
):

    db_timeline = crud.get_project_timeline_by_id(
        db,
        timeline_id
    )

    if not db_timeline:
        raise HTTPException(
            status_code=404,
            detail="Timeline event not found"
        )

    return crud.delete_project_timeline(
        db,
        db_timeline
    )