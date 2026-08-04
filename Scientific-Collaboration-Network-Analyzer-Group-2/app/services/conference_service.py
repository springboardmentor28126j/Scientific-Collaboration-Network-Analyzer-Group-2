from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.conference import Conference
from app.repositories.conference_repository import ConferenceRepository
from app.schemas.conference import (
    ConferenceCreate,
    ConferenceUpdate,
)


class ConferenceService:

    @staticmethod
    def create_conference(
        db: Session,
        data: ConferenceCreate,
    ):
        existing = ConferenceRepository.get_by_title(
            db,
            data.title,
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Conference already exists",
            )

        conference = Conference(
            **data.model_dump()
        )

        return ConferenceRepository.create(
            db,
            conference,
        )

    @staticmethod
    def get_all_conferences(
        db: Session,
    ):
        return ConferenceRepository.get_all(db)

    @staticmethod
    def get_conference(
        db: Session,
        conference_id: UUID,
    ):
        conference = ConferenceRepository.get_by_id(
            db,
            conference_id,
        )

        if conference is None:
            raise HTTPException(
                status_code=404,
                detail="Conference not found",
            )

        return conference

    @staticmethod
    def update_conference(
        db: Session,
        conference_id: UUID,
        data: ConferenceUpdate,
    ):
        conference = ConferenceRepository.get_by_id(
            db,
            conference_id,
        )

        if conference is None:
            raise HTTPException(
                status_code=404,
                detail="Conference not found",
            )

        updates = data.model_dump(exclude_unset=True)

        for key, value in updates.items():
            setattr(conference, key, value)

        db.commit()
        db.refresh(conference)

        return conference

    @staticmethod
    def delete_conference(
        db: Session,
        conference_id: UUID,
    ):
        conference = ConferenceRepository.get_by_id(
            db,
            conference_id,
        )

        if conference is None:
            raise HTTPException(
                status_code=404,
                detail="Conference not found",
            )

        ConferenceRepository.delete(
            db,
            conference,
        )

        return {
            "message": "Conference deleted successfully"
        }