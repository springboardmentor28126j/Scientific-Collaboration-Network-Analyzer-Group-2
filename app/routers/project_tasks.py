from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.schemas.project_task import (
    ProjectTaskCreate,
    ProjectTaskUpdate,
    ProjectTaskResponse
)

from app import crud

router = APIRouter(
    prefix="/project-tasks",
    tags=["Project Tasks"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get(
    "/",
    response_model=list[ProjectTaskResponse]
)
def get_all_tasks(
    db: Session = Depends(get_db)
):

    return crud.get_all_project_tasks(db)


@router.get(
    "/project/{project_id}",
    response_model=list[ProjectTaskResponse]
)
def get_project_tasks(
    project_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_tasks_by_project(
        db,
        project_id
    )


@router.get(
    "/member/{researcher_id}",
    response_model=list[ProjectTaskResponse]
)
def get_member_tasks(
    researcher_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_tasks_by_member(
        db,
        researcher_id
    )


@router.post(
    "/",
    response_model=ProjectTaskResponse
)
def create_task(
    task: ProjectTaskCreate,
    db: Session = Depends(get_db)
):

    return crud.create_project_task(
        db,
        task
    )


@router.put(
    "/{task_id}",
    response_model=ProjectTaskResponse
)
def update_task(
    task_id: int,
    task: ProjectTaskUpdate,
    db: Session = Depends(get_db)
):

    db_task = crud.get_project_task_by_id(
        db,
        task_id
    )

    if not db_task:

        raise HTTPException(
            status_code=404,
            detail="Project task not found"
        )

    return crud.update_project_task(
        db,
        db_task,
        task
    )


@router.delete(
    "/{task_id}"
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    db_task = crud.get_project_task_by_id(
        db,
        task_id
    )

    if not db_task:

        raise HTTPException(
            status_code=404,
            detail="Project task not found"
        )

    return crud.delete_project_task(
        db,
        db_task
    )