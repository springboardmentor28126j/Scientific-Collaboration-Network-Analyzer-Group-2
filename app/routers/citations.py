from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import traceback

from app.database.database import SessionLocal
from app.schemas.citation import (
    CitationCreate,
    CitationResponse
)
from app import crud

router = APIRouter(
    prefix="/citations",
    tags=["Citations"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get(
    "/",
    response_model=list[CitationResponse]
)
def get_all(
    db: Session = Depends(get_db)
):

    try:

        return crud.get_all_citations(db)

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/paper/{paper_id}",
    response_model=list[CitationResponse]
)
def get_by_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):

    try:

        return crud.get_citations_by_paper(
            db,
            paper_id
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post(
    "/",
    response_model=CitationResponse
)
def create(
    citation: CitationCreate,
    db: Session = Depends(get_db)
):

    try:

        return crud.create_citation(
            db,
            citation
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.delete("/{citation_id}")
def delete(
    citation_id: int,
    db: Session = Depends(get_db)
):

    try:

        citation = crud.get_citation_by_id(
            db,
            citation_id
        )

        if not citation:

            raise HTTPException(
                status_code=404,
                detail="Citation not found"
            )

        return crud.delete_citation(
            db,
            citation
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )