from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.schemas.project_document import (
    ProjectDocumentCreate,
    ProjectDocumentUpdate,
    ProjectDocumentResponse
)
from app import crud

router = APIRouter(
    prefix="/project-documents",
    tags=["Project Documents"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=list[ProjectDocumentResponse]
)
def get_all_documents(
    db: Session = Depends(get_db)
):
    return crud.get_all_project_documents(db)


@router.get(
    "/project/{project_id}",
    response_model=list[ProjectDocumentResponse]
)
def get_documents_by_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_project_documents_by_project(
        db,
        project_id
    )


@router.post(
    "/",
    response_model=ProjectDocumentResponse
)
def create_document(
    document: ProjectDocumentCreate,
    db: Session = Depends(get_db)
):
    return crud.create_project_document(
        db,
        document
    )


@router.put(
    "/{document_id}",
    response_model=ProjectDocumentResponse
)
def update_document(
    document_id: int,
    document: ProjectDocumentUpdate,
    db: Session = Depends(get_db)
):

    db_document = crud.get_project_document_by_id(
        db,
        document_id
    )

    if not db_document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return crud.update_project_document(
        db,
        db_document,
        document
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    db_document = crud.get_project_document_by_id(
        db,
        document_id
    )

    if not db_document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return crud.delete_project_document(
        db,
        db_document
    )