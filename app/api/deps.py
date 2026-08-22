"""
Wiring between routes and services. Routes depend on these factories
rather than importing services directly, so tests can override them
cleanly via FastAPI's dependency_overrides.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services.turnstile_service import TurnstileService
from app.services.auth_service import AuthService
from app.services.institution_service import InstitutionService
from app.services.notification_service import NotificationService
from app.services.publication_conference_service import PublicationConferenceService
from app.services.publication_conference_service import PublicationConferenceService
from app.services.publication_reference_service import PublicationReferenceService
from app.services.publication_indexing_service import PublicationIndexingService
from app.services.review_assignment_service import ReviewAssignmentService
from app.services.user_service import UserService
from app.services.publication_service import PublicationService
from app.services.publication_author_service import PublicationAuthorService
from app.services.review_service import ReviewService
from app.services.publication_history_service import PublicationHistoryService
from app.services.dashboard_service import DashboardService


def get_turnstile_service() -> TurnstileService:
    return TurnstileService()


def get_auth_service(
    session: AsyncSession = Depends(get_session),
    turnstile: TurnstileService = Depends(get_turnstile_service),
) -> AuthService:
    return AuthService(
        session,
        turnstile,
    )


def get_institution_service(
    session: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
    turnstile: TurnstileService = Depends(get_turnstile_service),
) -> InstitutionService:
    return InstitutionService(session, auth_service, turnstile)


def get_user_service(
    session: AsyncSession = Depends(get_session),
    turnstile: TurnstileService = Depends(get_turnstile_service),
) -> UserService:
    return UserService(session, turnstile)


def get_dashboard_service(
    session: AsyncSession = Depends(get_session),
) -> DashboardService:
    return DashboardService(session)


def get_publication_service(session: AsyncSession = Depends(get_session)) -> PublicationService:
    return PublicationService(session)


def get_publication_author_service(
    session: AsyncSession = Depends(get_session),
) -> PublicationAuthorService:
    return PublicationAuthorService(session)


def get_review_assignment_service(
    session: AsyncSession = Depends(get_session),
) -> ReviewAssignmentService:
    return ReviewAssignmentService(session)


def get_review_service(
    session: AsyncSession = Depends(get_session),
) -> ReviewService:
    return ReviewService(session)


def get_publication_history_service(
    session: AsyncSession = Depends(get_session),
) -> PublicationHistoryService:
    return PublicationHistoryService(session)


def get_publication_conference_service(
    session: AsyncSession = Depends(get_session),
) -> PublicationConferenceService:
    return PublicationConferenceService(session)


def get_publication_reference_service(
    session: AsyncSession = Depends(get_session),
) -> PublicationReferenceService:
    return PublicationReferenceService(session)


def get_publication_indexing_service(
    session: AsyncSession = Depends(get_session),
) -> PublicationIndexingService:
    return PublicationIndexingService(session)


def get_notification_service(
    session: AsyncSession = Depends(get_session),
) -> NotificationService:
    return NotificationService(session)
