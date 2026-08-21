"""
Importing every model module here ensures they're all registered on
Base.metadata before Alembic (or anything else) inspects it.
"""

from app.models.institution import Department, Institution
from app.models.research import (
    AuditLog,
    Citation,
    Conference,
    ConferenceEvent,
    ConferenceParticipation,
    InstitutionalCollaboration,
    Notification,
    Project,
    ProjectMember,
    Publication,
    PublicationAuthor,
    ResearcherProfile,
)
from app.models.token import EmailVerificationToken, PasswordResetToken, VerificationPurpose
from app.models.user import User, UserRole

__all__ = [
    "Institution",
    "Department",
    "User",
    "UserRole",
    "EmailVerificationToken",
    "PasswordResetToken",
    "VerificationPurpose",
    "ResearcherProfile",
    "Publication",
    "PublicationAuthor",
    "Project",
    "ProjectMember",
    "Conference",
    "ConferenceEvent",
    "ConferenceParticipation",
    "Citation",
    "InstitutionalCollaboration",
    "Notification",
    "AuditLog",
]
