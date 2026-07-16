"""
Importing every model module here ensures they're all registered on
Base.metadata before Alembic (or anything else) inspects it.
"""

from app.models.institution import Institution
from app.models.token import EmailVerificationToken, PasswordResetToken, VerificationPurpose
from app.models.user import User, UserRole
from app.models.publication import Publication, PublicationStatus
from app.models.publication_author import PublicationAuthor

__all__ = [
    "Institution",
    "User",
    "UserRole",
    "Publication",
    "PublicationAuthor",
    "PublicationStatus",
    "EmailVerificationToken",
    "PasswordResetToken",
    "VerificationPurpose",
]
