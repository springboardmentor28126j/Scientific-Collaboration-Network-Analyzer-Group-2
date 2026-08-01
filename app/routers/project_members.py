from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberUpdate,
    ProjectMemberResponse
)
from app import crud

router = APIRouter(
    prefix="/project-members",
    tags=["Project Members"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get(
    "/",
    response_model=list[ProjectMemberResponse]
)
def get_all_members(
    db: Session = Depends(get_db)
):

    return crud.get_all_project_members(db)


@router.get(
    "/project/{project_id}",
    response_model=list[ProjectMemberResponse]
)
def get_project_members(
    project_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_members_by_project(
        db,
        project_id
    )


@router.post(
    "/",
    response_model=ProjectMemberResponse
)
def create_member(
    member: ProjectMemberCreate,
    db: Session = Depends(get_db)
):

    return crud.create_project_member(
        db,
        member
    )


@router.put(
    "/{member_id}",
    response_model=ProjectMemberResponse
)
def update_member(
    member_id: int,
    member: ProjectMemberUpdate,
    db: Session = Depends(get_db)
):

    db_member = crud.get_project_member_by_id(
        db,
        member_id
    )

    if not db_member:

        raise HTTPException(
            status_code=404,
            detail="Project member not found"
        )

    return crud.update_project_member(
        db,
        db_member,
        member
    )


@router.delete(
    "/{member_id}"
)
def delete_member(
    member_id: int,
    db: Session = Depends(get_db)
):

    db_member = crud.get_project_member_by_id(
        db,
        member_id
    )

    if not db_member:

        raise HTTPException(
            status_code=404,
            detail="Project member not found"
        )

    return crud.delete_project_member(
        db,
        db_member
    )