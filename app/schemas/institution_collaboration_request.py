from pydantic import BaseModel
from datetime import datetime


class InstitutionCollaborationRequestBase(BaseModel):

    sender_institution_id: int
    receiver_institution_id: int
    project_title: str
    purpose: str


class InstitutionCollaborationRequestCreate(
    InstitutionCollaborationRequestBase
):
    pass


class InstitutionCollaborationRequestUpdate(BaseModel):

    status: str


class InstitutionCollaborationRequestResponse(
    InstitutionCollaborationRequestBase
):

    id: int

    sender_institution_name: str
    receiver_institution_name: str

    status: str
    created_at: datetime

    class Config:
        from_attributes = True