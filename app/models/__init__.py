"""
Importing every model module here ensures they're all registered on
Base.metadata before Alembic (or anything else) inspects it.
"""

from app.models.institution import Institution
from app.models.token import EmailVerificationToken, PasswordResetToken, VerificationPurpose
from app.models.user import User, UserRole
from app.models.publication import Publication, PublicationStatus
from app.models.publication_author import PublicationAuthor
from app.models.review_assignment import ReviewAssignment, ReviewAssignmentStatus
from app.models.review import Review, ReviewDecision
from app.models.publication_history import PublicationHistory, PublicationHistoryAction
from app.models.publication_conference import PublicationConference, ConferenceOutcome

__all__ = [
    "Institution",
    "User",
    "UserRole",
    "Publication",
    "PublicationAuthor",
    "PublicationStatus",
    "PublicationHistory",
    "PublicationConference",
    "ConferenceOutcome",
    "PublicationHistoryAction",
    "ReviewAssignment",
    "ReviewAssignmentStatus",
    "Review",
    "ReviewDecision",
    "EmailVerificationToken",
    "PasswordResetToken",
    "VerificationPurpose",
]
