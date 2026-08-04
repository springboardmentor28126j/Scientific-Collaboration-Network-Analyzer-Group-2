from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.researcher import Researcher
from app.repositories.researcher_repository import ResearcherRepository
from app.repositories.user_repository import UserRepository
from app.schemas.researcher import (
    ResearcherCreate,
    ResearcherUpdate,
)


class ResearcherService:

    @staticmethod
    def create_researcher(
        db: Session,
        researcher_data: ResearcherCreate,
    ):
        # Check if the user exists
        user = UserRepository.get_by_id(
            db,
            researcher_data.user_id,
        )

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        # Check if the user already has a researcher profile
        existing = ResearcherRepository.get_by_user_id(
            db,
            researcher_data.user_id,
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Researcher profile already exists",
            )

        researcher = Researcher(
            **researcher_data.model_dump()
        )

        return ResearcherRepository.create(
            db,
            researcher,
        )

    @staticmethod
    def get_all_researchers(
        db: Session,
    ):
        return ResearcherRepository.get_all(db)

    @staticmethod
    def get_researcher(
        db: Session,
        researcher_id: UUID,
    ):
        researcher = ResearcherRepository.get_by_id(
            db,
            researcher_id,
        )

        if researcher is None:
            raise HTTPException(
                status_code=404,
                detail="Researcher not found",
            )

        return researcher

    @staticmethod
    def update_researcher(
        db: Session,
        researcher_id: UUID,
        data: ResearcherUpdate,
    ):
        researcher = ResearcherRepository.get_by_id(
            db,
            researcher_id,
        )

        if researcher is None:
            raise HTTPException(
                status_code=404,
                detail="Researcher not found",
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                researcher,
                key,
                value,
            )

        return ResearcherRepository.update(
            db,
            researcher,
        )

    @staticmethod
    def delete_researcher(
        db: Session,
        researcher_id: UUID,
    ):
        researcher = ResearcherRepository.get_by_id(
            db,
            researcher_id,
        )

        if researcher is None:
            raise HTTPException(
                status_code=404,
                detail="Researcher not found",
            )

        ResearcherRepository.delete(
            db,
            researcher,
        )

        return {
            "message": "Researcher deleted successfully"
        }
