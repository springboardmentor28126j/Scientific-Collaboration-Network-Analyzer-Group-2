from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ResearcherBase(BaseModel):
    user_id: UUID
    institution_id: UUID
    department_id: UUID

    first_name: str
    last_name: str
    bio: str

    phone: Optional[str] = None
    experience: Optional[str] = None

    orcid: Optional[str] = None
    google_scholar: Optional[str] = None
    research_gate: Optional[str] = None
    linkedin: Optional[str] = None


class ResearcherCreate(ResearcherBase):
    pass


class ResearcherUpdate(BaseModel):
    institution_id: Optional[UUID] = None
    department_id: Optional[UUID] = None

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None

    phone: Optional[str] = None
    experience: Optional[str] = None

    orcid: Optional[str] = None
    google_scholar: Optional[str] = None
    research_gate: Optional[str] = None
    linkedin: Optional[str] = None


class ResearcherResponse(ResearcherBase):
    id: UUID

    model_config = ConfigDict(
        from_attributes=True
    )
