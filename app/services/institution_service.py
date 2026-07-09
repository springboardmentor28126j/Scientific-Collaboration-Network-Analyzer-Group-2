import uuid

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
from app.schemas.institution import InstitutionRegister
from app.services.auth_service import AuthService
from app.services.cloudinary_service import CloudinaryService
from app.services.email_service import EmailService


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
            is_active=True,
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
        await EmailService.send_institution_verification_email(
            admin.email, admin.full_name, verification_link
        )

        await self.session.commit()
        return institution, admin
    
    async def list_institutions(self) -> list[Institution]:
        return await self.institutions.list_all()

    async def set_institution_active(
        self, institution_id: uuid.UUID, is_active: bool
    ) -> Institution:
        institution = await self.institutions.get_by_id(institution_id)
        if institution is None:
            raise NotFoundError("Institution not found")
        institution = await self.institutions.set_active(institution, is_active)
        await self.session.commit()
        return institution
