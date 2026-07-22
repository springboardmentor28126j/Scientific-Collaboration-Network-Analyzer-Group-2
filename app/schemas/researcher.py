from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResearcherCreate(BaseModel):
    first_name: str
    last_name: str
    department_id: int | None = None
    academic_title: str | None = None
    orcid_id: str | None = None
    bio: str | None = None


class ResearcherUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    department_id: int | None = None
    academic_title: str | None = None
    orcid_id: str | None = None
    bio: str | None = None


class SkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_id: int
    name: str


class InterestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    interest_id: int
    name: str


class ResearcherOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    researcher_id: int
    user_id: int
    department_id: int | None
    first_name: str
    last_name: str
    academic_title: str | None
    orcid_id: str | None
    bio: str | None
    created_at: datetime
    # Model exposes these via `skill_objects`/`interest_objects` properties (flattened
    # from the researcher_skill/researcher_interest join tables); we present them to
    # API consumers under the friendlier names "skills" and "interests".
    skills: list[SkillOut] = Field(default_factory=list, validation_alias="skill_objects")
    interests: list[InterestOut] = Field(default_factory=list, validation_alias="interest_objects")


class SkillAdd(BaseModel):
    name: str


class InterestAdd(BaseModel):
    name: str
