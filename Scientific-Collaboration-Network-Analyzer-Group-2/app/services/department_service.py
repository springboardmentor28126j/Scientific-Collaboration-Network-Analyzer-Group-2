from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository
from app.repositories.institution_repository import InstitutionRepository
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
)


class DepartmentService:

    @staticmethod
    def create_department(
        db: Session,
        data: DepartmentCreate,
    ):
        institution = InstitutionRepository.get_by_id(
            db,
            data.institution_id,
        )

        if institution is None:
            raise HTTPException(
                status_code=404,
                detail="Institution not found",
            )

        department = Department(
            **data.model_dump()
        )

        return DepartmentRepository.create(
            db,
            department,
        )

    @staticmethod
    def get_all_departments(
        db: Session,
    ):
        return DepartmentRepository.get_all(db)

    @staticmethod
    def get_department(
        db: Session,
        department_id: UUID,
    ):
        department = DepartmentRepository.get_by_id(
            db,
            department_id,
        )

        if department is None:
            raise HTTPException(
                status_code=404,
                detail="Department not found",
            )

        return department

    @staticmethod
    def update_department(
        db: Session,
        department_id: UUID,
        data: DepartmentUpdate,
    ):
        department = DepartmentRepository.get_by_id(
            db,
            department_id,
        )

        if department is None:
            raise HTTPException(
                status_code=404,
                detail="Department not found",
            )

        updates = data.model_dump(exclude_unset=True)

        for key, value in updates.items():
            setattr(department, key, value)

        db.commit()
        db.refresh(department)

        return department

    @staticmethod
    def delete_department(
        db: Session,
        department_id: UUID,
    ):
        department = DepartmentRepository.get_by_id(
            db,
            department_id,
        )

        if department is None:
            raise HTTPException(
                status_code=404,
                detail="Department not found",
            )

        DepartmentRepository.delete(
            db,
            department,
        )

        return {
            "message": "Department deleted successfully"
        }
