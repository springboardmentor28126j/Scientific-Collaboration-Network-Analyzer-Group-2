from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.institution import Institution
from app.repositories.institution_repository import InstitutionRepository
from app.schemas.institution import (
    InstitutionCreate,
    InstitutionUpdate,
)


class InstitutionService:

    @staticmethod
    def create_institution(
        db: Session,
        data: InstitutionCreate,
    ):
        existing = InstitutionRepository.get_by_name(
            db,
            data.name,
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Institution already exists",
            )

        institution = Institution(
            **data.model_dump()
        )

        return InstitutionRepository.create(
            db,
            institution,
        )

    @staticmethod
    def get_all_institutions(
        db: Session,
    ):
        return InstitutionRepository.get_all(db)

    @staticmethod
    def get_institution(
        db: Session,
        institution_id: UUID,
    ):
        institution = InstitutionRepository.get_by_id(
            db,
            institution_id,
        )

        if institution is None:
            raise HTTPException(
                status_code=404,
                detail="Institution not found",
            )

        return institution

    @staticmethod
    def update_institution(
        db: Session,
        institution_id: UUID,
        data: InstitutionUpdate,
    ):
        institution = InstitutionRepository.get_by_id(
            db,
            institution_id,
        )

        if institution is None:
            raise HTTPException(
                status_code=404,
                detail="Institution not found",
            )

        updates = data.model_dump(exclude_unset=True)

        for key, value in updates.items():
            setattr(institution, key, value)

        db.commit()
        db.refresh(institution)

        return institution

    @staticmethod
    def delete_institution(
        db: Session,
        institution_id: UUID,
    ):
        institution = InstitutionRepository.get_by_id(
            db,
            institution_id,
        )

        if institution is None:
            raise HTTPException(
                status_code=404,
                detail="Institution not found",
            )

        InstitutionRepository.delete(
            db,
            institution,
        )

        return {
            "message": "Institution deleted successfully"
        }
