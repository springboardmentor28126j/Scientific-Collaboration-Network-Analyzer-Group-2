from pydantic import BaseModel

from app.models.user import UserRole


class AdminUserUpdate(BaseModel):
    """Fields a System Admin can change on any user account. Leave a field
    unset to leave it untouched."""
    role: UserRole | None = None
    is_active: bool | None = None