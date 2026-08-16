from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoleCounts(BaseModel):
    researcher: int = 0
    institution_admin: int = 0
    reviewer: int = 0
    system_admin: int = 0


class StatusCounts(BaseModel):
    """Generic label -> count map, used for publication/conference status breakdowns."""
    model_config = ConfigDict(extra="allow")


class DashboardStats(BaseModel):
    total_users: int
    users_by_role: RoleCounts
    total_institutions: int
    total_publications: int
    publications_by_status: dict[str, int]
    total_conferences: int
    conferences_by_status: dict[str, int]
    total_projects: int
    projects_by_status: dict[str, int]
    total_reviewers: int
    recent_audit_log_count: int


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    audit_id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    details: str | None
    ip_address: str | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogOut]
    total: int
    page: int
    page_size: int


class SystemSettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str | None
    description: str | None
    updated_by: int | None
    updated_at: datetime


class SystemSettingUpdate(BaseModel):
    value: str | None = None
    description: str | None = None
