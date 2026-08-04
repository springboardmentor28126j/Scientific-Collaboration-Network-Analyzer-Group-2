from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.models.user import (
    User,
    UserRole,
)
from app.models.researcher import Researcher

from app.repositories.user_repository import UserRepository

from app.schemas.user import UserCreate

from app.services.email_service import EmailService


class AuthService:

    # ---------------------------------------------------------
    # Register
    # ---------------------------------------------------------

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
            raise ValueError(
                "Email already registered."
            )

        verification_token = (
            EmailService.generate_verification_token()
        )

        verification_expiry = (
            EmailService.verification_expiry()
        )

        try:

            user = User(
                email=user_data.email,
                password_hash=hash_password(
                    user_data.password,
                ),
                role=user_data.role,
                is_active=False,
                email_verified=False,
                verification_token=verification_token,
                verification_token_expiry=verification_expiry,
            )

            db.add(user)
            db.flush()

            if user.role == UserRole.RESEARCHER:

                researcher = Researcher(
    user_id=user.id,
    first_name=user_data.first_name,
    last_name=user_data.last_name,
    experience=0,
)

                db.add(researcher)

            #EmailService.send_verification_email(
               # user.email,
               # verification_token,
            #)

            db.commit()

            db.refresh(user)

            return user

        except Exception:

            db.rollback()

            raise

    # ---------------------------------------------------------
    # Login
    # ---------------------------------------------------------

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

        if user is None:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        if not user.email_verified:
            raise ValueError(
                "Please verify your email first."
            )

        if not user.is_active:
            raise ValueError(
                "Your account is not active."
            )

        token = create_access_token(
            str(user.email)
        )

        return token


        # ---------------------------------------------------------
    # Verify Email
    # ---------------------------------------------------------

    @staticmethod
    def verify_email(
        db: Session,
        token: str,
    ):

        user = UserRepository.get_by_verification_token(
            db,
            token,
        )

        if user is None:
            raise ValueError(
                "Invalid verification token."
            )

        if user.email_verified:
            raise ValueError(
                "Email already verified."
            )

        if (
            user.verification_token_expiry is None
            or datetime.utcnow()
            > user.verification_token_expiry
        ):
            raise ValueError(
                "Verification token has expired."
            )

        user.email_verified = True
        user.is_active = True

        user.verification_token = None
        user.verification_token_expiry = None

        db.commit()
        db.refresh(user)

        return {
            "message": "Email verified successfully."
        }

    # ---------------------------------------------------------
    # Resend Verification Email
    # ---------------------------------------------------------

    @staticmethod
    def resend_verification(
        db: Session,
        email: str,
    ):

        user = UserRepository.get_by_email(
            db,
            email,
        )

        if user is None:
            raise ValueError(
                "User not found."
            )

        if user.email_verified:
            raise ValueError(
                "Email already verified."
            )

        token = (
            EmailService.generate_verification_token()
        )

        expiry = (
            EmailService.verification_expiry()
        )

        user.verification_token = token
        user.verification_token_expiry = expiry

        EmailService.send_verification_email(
            user.email,
            token,
        )

        db.commit()
        db.refresh(user)

        return {
            "message":
                "Verification email sent successfully."
        }

        # ---------------------------------------------------------
    # Forgot Password
    # ---------------------------------------------------------

    @staticmethod
    def forgot_password(
        db: Session,
        email: str,
    ):

        user = UserRepository.get_by_email(
            db,
            email,
        )

        # Return success even if the user doesn't exist
        # to avoid email enumeration.
        if user is None:
            return {
                "message": (
                    "If an account with that email exists, "
                    "a password reset email has been sent."
                )
            }

        token = EmailService.generate_reset_token()

        expiry = EmailService.reset_token_expiry()

        user.password_reset_token = token
        user.password_reset_expiry = expiry

        EmailService.send_reset_password_email(
            user.email,
            token,
        )

        db.commit()

        return {
            "message": (
                "If an account with that email exists, "
                "a password reset email has been sent."
            )
        }

    # ---------------------------------------------------------
    # Reset Password
    # ---------------------------------------------------------

    @staticmethod
    def reset_password(
        db: Session,
        token: str,
        new_password: str,
    ):

        user = UserRepository.get_by_reset_token(
            db,
            token,
        )

        if user is None:
            raise ValueError(
                "Invalid password reset token."
            )

        if (
            user.password_reset_expiry is None
            or datetime.utcnow()
            > user.password_reset_expiry
        ):
            raise ValueError(
                "Password reset token has expired."
            )

        user.password_hash = hash_password(
            new_password,
        )

        user.password_reset_token = None
        user.password_reset_expiry = None

        db.commit()
        db.refresh(user)

        return {
            "message": "Password reset successfully."
        }