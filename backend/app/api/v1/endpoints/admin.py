from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.models.conference import Conference
from app.models.institution import Institution
from app.models.publication import Publication
from app.models.project import Project
from app.models.user import User, UserRole
from app.repositories import audit_log_repository, system_setting_repository
from app.schemas.admin import (
    DashboardStats, RoleCounts, AuditLogListResponse, SystemSettingOut, SystemSettingUpdate,
)
from app.utils.audit import write_audit_log

router = APIRouter(prefix="/admin", tags=["Admin"])

# Every route in this file is System Admin only -- this is the platform-wide
# control surface (BR: "System Admin can access everything; no other role
# manages system settings, views all audit logs, or sees cross-institution stats").
_admin_only = Depends(require_roles(UserRole.SYSTEM_ADMIN))


@router.get("/dashboard-stats", response_model=DashboardStats)
def get_dashboard_stats(current_user: User = _admin_only, db: Session = Depends(get_db)):
    role_rows = db.execute(select(User.role, func.count()).group_by(User.role)).all()
    role_counts = {role.value: count for role, count in role_rows}
    users_by_role = RoleCounts(**{k: v for k, v in role_counts.items() if k in RoleCounts.model_fields})
    total_users = sum(role_counts.values())

    total_institutions = db.scalar(select(func.count()).select_from(Institution))

    pub_rows = db.execute(select(Publication.status, func.count()).group_by(Publication.status)).all()
    publications_by_status = {status_.value: count for status_, count in pub_rows}
    total_publications = sum(publications_by_status.values())

    conf_rows = db.execute(select(Conference.status, func.count()).group_by(Conference.status)).all()
    conferences_by_status = {status_.value: count for status_, count in conf_rows}
    total_conferences = sum(conferences_by_status.values())

    proj_rows = db.execute(select(Project.status, func.count()).group_by(Project.status)).all()
    projects_by_status = {status_.value: count for status_, count in proj_rows}
    total_projects = sum(projects_by_status.values())

    total_audit_log_count = audit_log_repository.count_all(db)

    return DashboardStats(
        total_users=total_users,
        users_by_role=users_by_role,
        total_institutions=total_institutions,
        total_publications=total_publications,
        publications_by_status=publications_by_status,
        total_conferences=total_conferences,
        conferences_by_status=conferences_by_status,
        total_projects=total_projects,
        projects_by_status=projects_by_status,
        total_reviewers=role_counts.get(UserRole.REVIEWER.value, 0),
        recent_audit_log_count=total_audit_log_count,
    )


@router.get("/audit-logs", response_model=AuditLogListResponse)
def list_audit_logs(
    user_id: int | None = Query(None),
    entity_type: str | None = Query(None),
    action: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    current_user: User = _admin_only,
    db: Session = Depends(get_db),
):
    items, total = audit_log_repository.list_audit_logs(
        db, user_id=user_id, entity_type=entity_type, action=action, page=page, page_size=page_size
    )
    return AuditLogListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/settings", response_model=list[SystemSettingOut])
def list_settings(current_user: User = _admin_only, db: Session = Depends(get_db)):
    return system_setting_repository.list_settings(db)


@router.put("/settings/{key}", response_model=SystemSettingOut)
def update_setting(
    key: str, payload: SystemSettingUpdate, current_user: User = _admin_only, db: Session = Depends(get_db)
):
    setting = system_setting_repository.upsert_setting(
        db, key=key, value=payload.value, description=payload.description, updated_by=current_user.user_id
    )
    write_audit_log(db, current_user.user_id, "UPDATE", "system_setting", setting.setting_id, details=f"key={key}")
    return setting
