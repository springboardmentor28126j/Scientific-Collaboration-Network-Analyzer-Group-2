"""Small, reusable backend authorization helpers.

The frontend menu improves usability, but these checks are the enforcement
layer: an authenticated user cannot call an administrator endpoint directly.
"""
from typing import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import auth, models
from app.database import get_db
from app.audit import record as record_audit

SYSTEM_ADMIN_ROLES = {"admin", "system admin"}


def current_user(
    token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    user = db.query(models.User).filter(models.User.id == auth.read_token_subject(token)).first()
    if not user or user.account_status != "active":
        if user:
            record_audit(db, action="unauthorized_access", entity_type="security", entity_id=user.id, user_id=user.id, actor_role=user.role, details=f"Inactive account status: {user.account_status}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="An active account is required")
    return user


def require_roles(*roles: str) -> Callable:
    allowed = {role.lower() for role in roles}

    def dependency(user: models.User = Depends(current_user), db: Session = Depends(get_db)) -> models.User:
        if user.role.lower() not in allowed:
            record_audit(db, action="unauthorized_access", entity_type="security", entity_id=user.id, user_id=user.id, actor_role=user.role, details=f"Required role: {', '.join(sorted(allowed))}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission for this action")
        return user

    return dependency


def require_system_admin(user: models.User = Depends(current_user), db: Session = Depends(get_db)) -> models.User:
    if user.role.lower() not in SYSTEM_ADMIN_ROLES:
        record_audit(db, action="unauthorized_access", entity_type="security", entity_id=user.id, user_id=user.id, actor_role=user.role, details="System administrator role required")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="System administrator access is required")
    return user


def is_system_admin(user: models.User) -> bool:
    return user.role.lower() in SYSTEM_ADMIN_ROLES


def scoped_researchers_query(db: Session, user: models.User):
    query = db.query(models.Researcher)
    if is_system_admin(user) or user.role.lower() in {"publisher", "reviewer"}:
        return query
    if user.role.lower() == "institution admin":
        return query.filter(models.Researcher.institution_id == user.institution_id) if user.institution_id else query.filter(False)
    return query.filter(models.Researcher.id == user.researcher_id) if user.researcher_id else query.filter(False)


def scoped_publications_query(db: Session, user: models.User):
    query = db.query(models.Publication)
    if is_system_admin(user) or user.role.lower() == "publisher":
        return query
    if user.role.lower() == "reviewer":
        return query.join(models.ReviewAssignment).filter(models.ReviewAssignment.reviewer_id == user.id)
    if user.role.lower() == "institution admin":
        return query.filter(models.Publication.institution_id == user.institution_id) if user.institution_id else query.filter(False)
    return query.filter(models.Publication.authors.any(models.Researcher.id == user.researcher_id)) if user.researcher_id else query.filter(False)


def scoped_collaborations_query(db: Session, user: models.User):
    query = db.query(models.Collaboration)
    if is_system_admin(user) or user.role.lower() in {"publisher", "reviewer"}:
        return query
    if user.role.lower() == "institution admin":
        if not user.institution_id:
            return query.filter(False)
        researcher_ids = [row.id for row in db.query(models.Researcher.id).filter(models.Researcher.institution_id == user.institution_id).all()]
        return query.filter((models.Collaboration.researcher1_id.in_(researcher_ids)) | (models.Collaboration.researcher2_id.in_(researcher_ids)))
    return query.filter((models.Collaboration.researcher1_id == user.researcher_id) | (models.Collaboration.researcher2_id == user.researcher_id)) if user.researcher_id else query.filter(False)


def scoped_projects_query(db: Session, user: models.User):
    query = db.query(models.Project)
    if is_system_admin(user) or user.role.lower() in {"publisher", "reviewer"}:
        return query
    if user.role.lower() == "institution admin":
        return query.filter(models.Project.institution_id == user.institution_id) if user.institution_id else query.filter(False)
    return query.join(models.ProjectAssignment).filter(models.ProjectAssignment.researcher_id == user.researcher_id) if user.researcher_id else query.filter(False)
