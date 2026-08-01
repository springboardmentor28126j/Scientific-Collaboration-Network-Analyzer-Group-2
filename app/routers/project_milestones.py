from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.schemas.project_milestone import (
    ProjectMilestoneCreate,
    ProjectMilestoneUpdate,
    ProjectMilestoneResponse
)

from app import crud

router = APIRouter(
    prefix="/project-milestones",
    tags=["Project Milestones"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get(
    "/",
    response_model=list[ProjectMilestoneResponse]
)
def get_all_milestones(
    db: Session = Depends(get_db)
):

    return crud.get_all_project_milestones(db)


@router.get(
    "/project/{project_id}",
    response_model=list[ProjectMilestoneResponse]
)
def get_project_milestones(
    project_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_milestones_by_project(
        db,
        project_id
    )


@router.post(
    "/",
    response_model=ProjectMilestoneResponse
)
def create_milestone(
    milestone: ProjectMilestoneCreate,
    db: Session = Depends(get_db)
):

    return crud.create_project_milestone(
        db,
        milestone
    )


@router.put(
    "/{milestone_id}",
    response_model=ProjectMilestoneResponse
)
def update_milestone(
    milestone_id: int,
    milestone: ProjectMilestoneUpdate,
    db: Session = Depends(get_db)
):

    db_milestone = crud.get_project_milestone_by_id(
        db,
        milestone_id
    )

    if not db_milestone:

        raise HTTPException(
            status_code=404,
            detail="Project milestone not found"
        )

    return crud.update_project_milestone(
        db,
        db_milestone,
        milestone
    )


@router.delete(
    "/{milestone_id}"
)
def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db)
):

    db_milestone = crud.get_project_milestone_by_id(
        db,
        milestone_id
    )

    if not db_milestone:

        raise HTTPException(
            status_code=404,
            detail="Project milestone not found"
        )

    return crud.delete_project_milestone(
        db,
        db_milestone
    )