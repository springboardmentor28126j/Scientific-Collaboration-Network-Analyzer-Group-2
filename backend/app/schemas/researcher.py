from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserOut


class ResearcherBase(BaseModel):
    institution_id: int | None = None
    department: str | None = None
    research_interests: str | None = None
    skills: str | None = None
    affiliations: str | None = None


class ResearcherCreate(ResearcherBase):
    pass


class ResearcherUpdate(ResearcherBase):
    pass


class ResearcherOut(ResearcherBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user: UserOut
