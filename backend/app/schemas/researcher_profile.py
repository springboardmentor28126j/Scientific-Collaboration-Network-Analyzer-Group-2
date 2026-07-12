from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResearcherProfileBase(BaseModel):
    department: str | None = None
    designation: str | None = None
    bio: str | None = None
    research_interests: str | None = None
    skills: str | None = None
    phone: str | None = None
    orcid_id: str | None = None


class ResearcherProfileUpdate(ResearcherProfileBase):
    pass


class ResearcherProfileRead(ResearcherProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
