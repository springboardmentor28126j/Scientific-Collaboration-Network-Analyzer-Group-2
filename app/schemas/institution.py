from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InstitutionCreate(BaseModel):
    name: str
    type: str | None = None
    country: str | None = None
    address: str | None = None
    email_domain: str | None = None


class InstitutionUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    country: str | None = None
    address: str | None = None
    email_domain: str | None = None


class InstitutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    institution_id: int
    name: str
    type: str | None
    country: str | None
    address: str | None
    email_domain: str | None
    created_at: datetime


class DepartmentCreate(BaseModel):
    name: str
    code: str | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = None
    code: str | None = None


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    department_id: int
    institution_id: int
    name: str
    code: str | None