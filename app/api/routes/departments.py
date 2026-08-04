from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    get_current_user,
)

from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)

from app.services.department_service import DepartmentService

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=201,
)
def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DepartmentService.create_department(
        db,
        department,
    )


@router.get(
    "/",
    response_model=list[DepartmentResponse],
)
def get_departments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DepartmentService.get_all_departments(db)


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def get_department(
    department_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DepartmentService.get_department(
        db,
        department_id,
    )


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def update_department(
    department_id: UUID,
    department: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DepartmentService.update_department(
        db,
        department_id,
        department,
    )


@router.delete(
    "/{department_id}",
)
def delete_department(
    department_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DepartmentService.delete_department(
        db,
        department_id,
    )
