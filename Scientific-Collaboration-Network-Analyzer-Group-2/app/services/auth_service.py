from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.models.user import User

from app.repositories.user_repository import UserRepository

from app.schemas.user import UserCreate


class AuthService:

    @staticmethod
    def register(
        db: Session,
        user_data: UserCreate,
    ):

        existing_user = UserRepository.get_by_email(
            db,
            user_data.email,
        )

        if existing_user:
            raise ValueError("Email already exists")

        user = User(
            email=user_data.email,
            password_hash=hash_password(
                user_data.password
            ),
            role=user_data.role,
        )

        return UserRepository.create(
            db,
            user,
        )

    @staticmethod
    def login(
        db: Session,
        email: str,
        password: str,
    ):

        user = UserRepository.get_by_email(
            db,
            email,
        )

        if not user:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        token = create_access_token(
            str(user.email)
        )

        return token
