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
from app.models.audit_log import AuditLog