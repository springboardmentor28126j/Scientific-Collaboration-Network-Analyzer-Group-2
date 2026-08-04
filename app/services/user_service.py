from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository

from app.core.security import hash_password


class UserService:

    @staticmethod
    def get_all_users(db: Session):
        return UserRepository.get_all(db)

    @staticmethod
    def get_user(db: Session, user_id: UUID):
        return UserRepository.get_by_id(db, user_id)

    @staticmethod
    def update_user(
        db: Session,
        user,
        data,
    ):

        if data.email:
            user.email = data.email

        if data.password:
            user.password_hash = hash_password(
                data.password
            )

        return UserRepository.update(
            db,
            user,
        )

    @staticmethod
    def delete_user(
        db: Session,
        user,
    ):
        UserRepository.delete(
            db,
            user,
        )
