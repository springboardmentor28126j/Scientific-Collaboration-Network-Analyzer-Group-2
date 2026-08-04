from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    get_current_user,
)

from app.schemas.institution import (
    InstitutionCreate,
    InstitutionUpdate,
    InstitutionResponse,
)

from app.services.institution_service import InstitutionService

router = APIRouter(
    prefix="/institutions",
    tags=["Institutions"],
)


@router.post(
    "/",
    response_model=InstitutionResponse,
    status_code=201,
)
def create_institution(
    institution: InstitutionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return InstitutionService.create_institution(
        db,
        institution,
    )


@router.get(
    "/",
    response_model=list[InstitutionResponse],
)
def get_institutions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return InstitutionService.get_all_institutions(db)


@router.get(
    "/{institution_id}",
    response_model=InstitutionResponse,
)
def get_institution(
    institution_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return InstitutionService.get_institution(
        db,
        institution_id,
    )


@router.put(
    "/{institution_id}",
    response_model=InstitutionResponse,
)
def update_institution(
    institution_id: UUID,
    institution: InstitutionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return InstitutionService.update_institution(
        db,
        institution_id,
        institution,
    )


@router.delete(
    "/{institution_id}",
)
def delete_institution(
    institution_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return InstitutionService.delete_institution(
        db,
        institution_id,
    )
