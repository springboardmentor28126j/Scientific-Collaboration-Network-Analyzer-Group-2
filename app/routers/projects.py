from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import traceback

from app.database.database import SessionLocal
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse
)
from app import crud

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get(
    "/",
    response_model=list[ProjectResponse]
)
def get_projects(
    db: Session = Depends(get_db)
):

    return crud.get_all_projects(db)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    project = crud.get_project_by_id(
        db,
        project_id
    )

    if not project:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


@router.post(
    "/",
    response_model=ProjectResponse
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):

    try:

        return crud.create_project(
            db,
            project
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse
)
def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db)
):

    db_project = crud.get_project_by_id(
        db,
        project_id
    )

    if not db_project:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return crud.update_project(
        db,
        db_project,
        project
    )


@router.delete(
    "/{project_id}"
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    db_project = crud.get_project_by_id(
        db,
        project_id
    )

    if not db_project:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return crud.delete_project(
        db,
        db_project
    )