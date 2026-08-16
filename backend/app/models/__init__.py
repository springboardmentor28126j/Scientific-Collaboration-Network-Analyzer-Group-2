"""
Import all models here so that Alembic's autogenerate and Base.metadata
can discover every table, even ones not directly imported elsewhere.
"""
from app.models.institution import Institution, Department  # noqa: F401
from app.models.user import User, UserRole  # noqa: F401
from app.models.researcher import (
    ResearcherProfile,
    Skill,
    ResearcherSkill,
    ResearchInterest,
    ResearcherInterest
)
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.publication import Publication, PublicationAuthor, PublicationType, PublicationStatus  # noqa: F401
from app.models.conference import (  # noqa: F401
    Conference, ConferenceParticipation, ParticipationRole, SubmissionStatus, ConferenceStatus,
)
from app.models.system_setting import SystemSetting  # noqa: F401
from app.models.review import Review, ReviewTargetType, ReviewStatus, ReviewRecommendation  # noqa: F401
from app.models.project import Project, ProjectMember, ProjectStatus, ProjectMemberRole  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.institution_request import InstitutionRequest  # noqa: F401
from app.models.collaboration import Collaboration, CollaborationPublication, CollaborationRequest, CollaborationRequestStatus  # noqa: F401
from app.models.citation import Citation  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.project import Project, ProjectMember, ProjectStatus, ProjectMemberRole, ProjectMemberStatus, ProjectMessage  # noqa: F401