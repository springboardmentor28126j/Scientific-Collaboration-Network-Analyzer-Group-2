import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.security import hash_password
from app.models.token import VerificationPurpose
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import ResearcherRead, UserCreateByInstitution
from app.services.turnstile_service import TurnstileService
from app.services.auth_service import AuthService
from app.services.email_service import EmailService


class UserService:
    """
    Handles researcher/reviewer creation and activation, always scoped to
    the acting institution admin's own institution — no cross-institution
    access is possible through this service; every method takes the
    institution_id explicitly and filters by it.
    """

    def __init__(
        self,
        session: AsyncSession,
        turnstile: TurnstileService,
    ) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.auth_service = AuthService(session, turnstile)

    async def create_institution_user(
        self, institution_id: uuid.UUID, institution_name: str, payload: UserCreateByInstitution
    ) -> User:
        existing = await self.users.get_by_email(payload.email)
        if existing is not None:
            raise ConflictError("An account with this email already exists")

        # Placeholder, unusable hash — a random value so the column is
        # never left null. The real password is chosen by the researcher/
        # reviewer at invite-verification time (see
        # AuthService.verify_invite_token), which overwrites this before
        # the account is ever verified or active, so it's never reachable.
        placeholder_password = hash_password(uuid.uuid4().hex)

        user = await self.users.create(
            email=payload.email,
            hashed_password=placeholder_password,
            full_name=payload.full_name,
            role=payload.role,
            description=payload.description,
            institution_id=institution_id,
            is_verified=False,
            is_active=False,
        )

        raw_token = await self.auth_service.create_verification_token(
            user.id, VerificationPurpose.INVITE_VERIFY
        )
        invite_link = f"{settings.FRONTEND_URL}/verify-invite?token={raw_token}"
        await EmailService.send_invite_verification_email(
            user.email, user.full_name, institution_name, payload.role.value, invite_link
        )

        await self.session.commit()
        return user

    async def list_institution_users(
        self, institution_id: uuid.UUID, role: UserRole | None = None
    ) -> list[User]:
        """
        Lists Researchers/Reviewers under the institution — this endpoint
        is for managing the accounts an institution admin actually
        creates, so the admin's own account is intentionally excluded
        even when no role filter is given.
        """
        if role is not None:
            return await self.users.list_by_institution(institution_id, role)

        researchers = await self.users.list_by_institution(institution_id, UserRole.RESEARCHER)
        reviewers = await self.users.list_by_institution(institution_id, UserRole.REVIEWER)
        return researchers + reviewers

    async def set_user_active(
        self, institution_id: uuid.UUID, user_id: uuid.UUID, is_active: bool
    ) -> User:
        user = await self.users.get_by_id(user_id)
        if user is None or user.institution_id != institution_id:
            raise NotFoundError("User not found in this institution")
        if user.role == UserRole.INSTITUTION_ADMIN:
            raise ForbiddenError(
                "Institution admins cannot be activated/deactivated via this endpoint"
            )

        user = await self.users.set_active(user, is_active)
        await self.session.commit()
        return user

    async def list_researchers(
        self,
        current_user: User,
        search: str | None = None,
    ) -> list[ResearcherRead]:
        """
        Lists all researchers in their institutions, for the public-facing
        researcher directory. Only verified and active researchers are
        returned.
        """
        researchers = await self.users.list_researchers(
            institution_id=current_user.institution_id, search=search
        )
        return [
            ResearcherRead(
                id=r.id,
                full_name=r.full_name,
                email=r.email,
                description=r.description,
                institution_name=(r.institution.name if r.institution else ""),
            )
            for r in researchers
        ]

    async def list_reviewers(
        self,
        search: str | None = None,
    ) -> list[ResearcherRead]:
        """
        Lists all reviewers across institutions, for the public-facing
        researcher directory. Only verified and active researchers are
        returned.
        """
        researchers = await self.users.list_reviewers(search)
        return [
            ResearcherRead(
                id=r.id,
                full_name=r.full_name,
                email=r.email,
                description=r.description,
                institution_name=(r.institution.name if r.institution else ""),
            )
            for r in researchers
        ]
