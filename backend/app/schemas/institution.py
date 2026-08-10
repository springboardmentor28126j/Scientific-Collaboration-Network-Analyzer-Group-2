from pydantic import BaseModel, EmailStr, ConfigDict


class InstitutionBase(BaseModel):
    name: str
    short_name: str | None = None
    institution_type: str | None = None

    email: EmailStr
    phone: str | None = None
    website: str | None = None

    address: str | None = None
    city: str
    state: str
    country: str
    postal_code: str | None = None

    status: str = "Active"


class InstitutionCreate(InstitutionBase):
    # Only a System Admin can create an institution (enforced in the route),
    # and they choose who administers it. Optional so a System Admin can
    # create the record first and assign an admin later.
    admin_user_id: int | None = None


class InstitutionUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    institution_type: str | None = None

    email: EmailStr | None = None
    phone: str | None = None
    website: str | None = None

    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None

    status: str | None = None
    admin_user_id: int | None = None


class InstitutionOut(InstitutionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    admin_user_id: int | None = None
