import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **fields) -> User:
        user = User(**fields)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.institution)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.institution)).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def list_by_institution(
        self, institution_id: uuid.UUID, role: UserRole | None = None
    ) -> list[User]:
        stmt = select(User).where(User.institution_id == institution_id)
        if role is not None:
            stmt = stmt.where(User.role == role)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_verified_and_active(self, user: User) -> User:
        """Verification auto-activates — see docs/architecture.md §5."""
        user.is_verified = True
        user.is_active = True
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def set_active(self, user: User, is_active: bool) -> User:
        user.is_active = is_active
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def set_password(self, user: User, hashed_password: str) -> User:
        user.hashed_password = hashed_password
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def list_researchers(
        self,
        search: str | None = None,
    ) -> list[User]:
        stmt = (
            select(User)
            .options(selectinload(User.institution))
            .where(
                User.role == UserRole.RESEARCHER,
                User.is_active.is_(True),
                User.is_verified.is_(True),
            )
            .order_by(User.full_name.asc())
        )

        if search:
            stmt = stmt.where(
                or_(
                    User.full_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                )
            )
        result = await self.session.execute(stmt)
        print(result)
        return list(result.scalars().all())
