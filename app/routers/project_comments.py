from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.schemas.project_comment import (
    ProjectCommentCreate,
    ProjectCommentUpdate,
    ProjectCommentResponse
)
from app import crud

router = APIRouter(
    prefix="/project-comments",
    tags=["Project Comments"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=list[ProjectCommentResponse]
)
def get_all_comments(
    db: Session = Depends(get_db)
):
    return crud.get_all_project_comments(db)


@router.get(
    "/project/{project_id}",
    response_model=list[ProjectCommentResponse]
)
def get_comments_by_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_comments_by_project(
        db,
        project_id
    )


@router.post(
    "/",
    response_model=ProjectCommentResponse
)
def create_comment(
    comment: ProjectCommentCreate,
    db: Session = Depends(get_db)
):
    return crud.create_project_comment(
        db,
        comment
    )


@router.put(
    "/{comment_id}",
    response_model=ProjectCommentResponse
)
def update_comment(
    comment_id: int,
    comment: ProjectCommentUpdate,
    db: Session = Depends(get_db)
):

    db_comment = crud.get_project_comment_by_id(
        db,
        comment_id
    )

    if not db_comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    return crud.update_project_comment(
        db,
        db_comment,
        comment
    )


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):

    db_comment = crud.get_project_comment_by_id(
        db,
        comment_id
    )

    if not db_comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    return crud.delete_project_comment(
        db,
        db_comment
    )