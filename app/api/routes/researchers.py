from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    get_current_user,
)

from app.schemas.researcher import (
    ResearcherCreate,
    ResearcherUpdate,
    ResearcherResponse,
)

from app.services.researcher_service import ResearcherService

router = APIRouter(
    prefix="/researchers",
    tags=["Researchers"],
)


@router.post(
    "/",
    response_model=ResearcherResponse,
    status_code=201,
)
def create_researcher(
    researcher: ResearcherCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ResearcherService.create_researcher(
        db,
        researcher,
    )


@router.get(
    "/",
    response_model=list[ResearcherResponse],
)
def get_researchers(
    db: Session = Depends(get_db),
):
    return ResearcherService.get_all_researchers(
        db,
    )


@router.get(
    "/{researcher_id}",
    response_model=ResearcherResponse,
)
def get_researcher(
    researcher_id: UUID,
    db: Session = Depends(get_db),
):
    return ResearcherService.get_researcher(
        db,
        researcher_id,
    )


@router.put(
    "/{researcher_id}",
    response_model=ResearcherResponse,
)
def update_researcher(
    researcher_id: UUID,
    researcher: ResearcherUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ResearcherService.update_researcher(
        db,
        researcher_id,
        researcher,
    )


@router.delete(
    "/{researcher_id}",
)
def delete_researcher(
    researcher_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ResearcherService.delete_researcher(
        db,
        researcher_id,
    )
