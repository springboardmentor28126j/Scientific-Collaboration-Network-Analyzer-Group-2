from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.institution_collaboration import InstitutionCollaborationStatus


class InstitutionBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    short_name: str | None = None


class InstitutionCollaborationCreate(BaseModel):
    partner_institution_id: int
    title: str = Field(max_length=500)
    description: str | None = Field(default=None, max_length=2000)
    start_date: date | None = None
    end_date: date | None = None


class InstitutionCollaborationStatusUpdate(BaseModel):
    status: InstitutionCollaborationStatus


class InstitutionCollaborationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    institution1: InstitutionBrief
    institution2: InstitutionBrief
    title: str
    description: str | None
    status: InstitutionCollaborationStatus
    start_date: date | None
    end_date: date | None
    created_at: datetime