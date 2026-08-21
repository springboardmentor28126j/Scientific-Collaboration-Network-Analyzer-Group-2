import uuid
import logging

from sqlalchemy import select
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.institution import Institution
from app.models.token import VerificationPurpose
from app.models.user import User, UserRole
from app.repositories.institution_repository import InstitutionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.institution import InstitutionCreate, InstitutionRegister, InstitutionUpdate
from app.services.auth_service import AuthService
from app.services.cloudinary_service import CloudinaryService
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class InstitutionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.institutions = InstitutionRepository(session)
        self.users = UserRepository(session)
        self.auth_service = AuthService(session)

    async def register(
        self, payload: InstitutionRegister, logo_file: UploadFile
    ) -> tuple[Institution, User]:
        existing = await self.users.get_by_email(payload.admin_email)
        if existing is not None:
            raise ConflictError("An account with this email already exists")

        logo_url, logo_public_id = await CloudinaryService.upload_institution_logo(logo_file)

        institution = await self.institutions.create(
            name=payload.name,
            address=payload.address,
            logo_url=logo_url,
            logo_public_id=logo_public_id,
            is_active=False,
        )

        admin = await self.users.create(
            email=payload.admin_email,
            hashed_password=hash_password(payload.admin_password),
            full_name=payload.admin_full_name,
            role=UserRole.INSTITUTION_ADMIN,
            institution_id=institution.id,
            is_verified=False,
            is_active=False,
        )

        raw_token = await self.auth_service.create_verification_token(
            admin.id, VerificationPurpose.EMAIL_VERIFY
        )
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={raw_token}"
        await self.session.commit()
        try:
            await EmailService.send_institution_verification_email(
                admin.email, admin.full_name, verification_link
            )
        except Exception:
            logger.exception("Institution registered but verification email could not be sent: %s", verification_link)
        return institution, admin
    
    async def list_institutions(self) -> list[Institution]:
        return await self.institutions.list_all()

    async def create_platform_institution(self, payload: InstitutionCreate) -> Institution:
        institution = await self.institutions.create(**payload.model_dump(), is_active=True)
        await self.session.commit()
        await self.session.refresh(institution)
        return institution

    async def get_institution(self, institution_id: uuid.UUID) -> Institution:
        institution = await self.institutions.get_by_id(institution_id)
        if institution is None:
            raise NotFoundError("Institution not found")
        return institution

    async def update_institution(self, institution_id: uuid.UUID, payload: InstitutionUpdate) -> Institution:
        institution = await self.get_institution(institution_id)
        for field, value in payload.model_dump().items():
            setattr(institution, field, value)
        await self.session.commit()
        await self.session.refresh(institution)
        return institution

    async def delete_institution(self, institution_id: uuid.UUID) -> None:
        institution = await self.get_institution(institution_id)
        await self.session.delete(institution)
        await self.session.commit()

    async def set_institution_active(
        self, institution_id: uuid.UUID, is_active: bool
    ) -> Institution:
        institution = await self.institutions.get_by_id(institution_id)
        if institution is None:
            raise NotFoundError("Institution not found")

        institution.is_active = is_active
        if is_active:
            admin = await self.session.scalar(
                select(User).where(
                    User.institution_id == institution.id,
                    User.role == UserRole.INSTITUTION_ADMIN,
                )
            )
            if admin is not None:
                admin.is_verified = True
                admin.is_active = True

        await self.session.commit()
        await self.session.refresh(institution)
        return institution
