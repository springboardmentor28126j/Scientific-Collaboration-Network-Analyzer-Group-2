from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.search_service import SearchService

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("")
def search(
    q: str = Query(..., min_length=1),
    type: str = Query("all"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),

    # Advanced Filters
    year: Optional[int] = Query(None),
    publication_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    institution: Optional[str] = Query(None),
    sort: str = Query("relevance"),

    db: Session = Depends(get_db),
):
    return SearchService.search(
        db=db,
        query=q,
        entity_type=type,
        page=page,
        page_size=page_size,
        year=year,
        publication_type=publication_type,
        status=status,
        institution=institution,
        sort=sort,
    )
