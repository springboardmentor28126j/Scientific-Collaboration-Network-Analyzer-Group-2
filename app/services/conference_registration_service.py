from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.conference_registration_repository import (
    ConferenceRegistrationRepository,
)
from app.services.conference_service import ConferenceService


class ConferenceRegistrationService:

    @staticmethod
    def join_conference(
        db: Session,
        conference_id: UUID,
        current_user: User,
    ):
        # Verify conference exists
        ConferenceService.get_conference(db = db, conference_id=conference_id,)

        # Prevent duplicate registration
        existing = ConferenceRegistrationRepository.get_registration(
            db=db,
            conference_id=conference_id,
            user_id=current_user.id,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already joined this conference.",
            )

        return ConferenceRegistrationRepository.create(
            db=db,
            conference_id=conference_id,
            user_id=current_user.id,
        )

    @staticmethod
    def leave_conference(
        db: Session,
        conference_id: UUID,
        current_user: User,
    ):
        registration = ConferenceRegistrationRepository.get_registration(
            db=db,
            conference_id=conference_id,
            user_id=current_user.id,
        )

        if registration is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You are not registered for this conference.",
            )

        ConferenceRegistrationRepository.delete(
            db=db,
            registration=registration,
        )

        return {
            "message": "Successfully left the conference."
        }

    @staticmethod
    def get_joined_conferences(
        db: Session,
        current_user: User,
    ):
        registrations = (
            ConferenceRegistrationRepository.get_user_registrations(
                db=db,
                user_id=current_user.id,
            )
        )

        return [registration.conference for registration in registrations]

    @staticmethod
    def participant_count(
        db: Session,
        conference_id: UUID,
    ):
        return ConferenceRegistrationRepository.count_participants(
            db=db,
            conference_id=conference_id,
        )
