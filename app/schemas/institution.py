from pydantic import BaseModel


class InstitutionBase(BaseModel):
    institution_name: str
    country: str
    city: str
    website: str | None = None
    established_year: int | None = None


class InstitutionCreate(InstitutionBase):
    pass


class InstitutionResponse(InstitutionBase):
    id: int

    class Config:
        from_attributes = True