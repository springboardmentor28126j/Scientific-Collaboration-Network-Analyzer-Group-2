from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.institution import Institution, Department
from app.models.user import User, UserRole
from app.schemas.institution import (
    InstitutionCreate, InstitutionOut, InstitutionUpdate,
    DepartmentCreate, DepartmentUpdate, DepartmentOut,
)
from app.utils.audit import write_audit_log

router = APIRouter(prefix="/institutions", tags=["Institutions"])


@router.get("", response_model=list[InstitutionOut])
def list_institutions(
    name: str | None = Query(None, description="Case-insensitive partial match on institution name"),
    country: str | None = Query(None),
    type: str | None = Query(None, description="e.g. university, lab, publisher, funding_org"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    # Deliberately public (no auth) -- the registration form needs to show
    # institution options before a user has an account or token.
    # Institution names/types aren't sensitive data.
    stmt = select(Institution)
    if name:
        stmt = stmt.where(Institution.name.ilike(f"%{name}%"))
    if country:
        stmt = stmt.where(Institution.country == country)
    if type:
        stmt = stmt.where(Institution.type == type)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.post("", response_model=InstitutionOut, status_code=201)
def create_institution(
    payload: InstitutionCreate,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
):
    institution = Institution(**payload.model_dump())
    db.add(institution)
    db.commit()
    db.refresh(institution)
    write_audit_log(db, current_user.user_id, "CREATE", "institution", institution.institution_id)
    return institution


@router.get("/{institution_id}", response_model=InstitutionOut)
def get_institution(institution_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    institution = db.get(Institution, institution_id)
    if institution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
    return institution


@router.patch("/{institution_id}", response_model=InstitutionOut)
def update_institution(
    institution_id: int,
    payload: InstitutionUpdate,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    institution = db.get(Institution, institution_id)
    if institution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
    if current_user.role == UserRole.INSTITUTION_ADMIN and current_user.institution_id != institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit another institution")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(institution, field, value)
    db.commit()
    db.refresh(institution)
    write_audit_log(db, current_user.user_id, "UPDATE", "institution", institution.institution_id)
    return institution


@router.delete("/{institution_id}", status_code=204)
def delete_institution(
    institution_id: int,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
):
    institution = db.get(Institution, institution_id)
    if institution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    # Log before deleting -- the row (and its id) won't exist to reference afterward.
    write_audit_log(db, current_user.user_id, "DELETE", "institution", institution_id)
    # Departments cascade-delete (cascade="all, delete-orphan" on the relationship).
    # Users keep existing -- their institution_id is set NULL via ondelete="SET NULL"
    # on the FK, so deleting an institution never deletes user accounts.
    db.delete(institution)
    db.commit()
    return None


@router.get("/{institution_id}/departments", response_model=list[DepartmentOut])
def list_departments(institution_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list(db.scalars(select(Department).where(Department.institution_id == institution_id)).all())


@router.post("/{institution_id}/departments", response_model=DepartmentOut, status_code=201)
def create_department(
    institution_id: int,
    payload: DepartmentCreate,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.INSTITUTION_ADMIN and current_user.institution_id != institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot add departments to another institution")

    department = Department(institution_id=institution_id, **payload.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    write_audit_log(db, current_user.user_id, "CREATE", "department", department.department_id)
    return department


@router.patch("/{institution_id}/departments/{department_id}", response_model=DepartmentOut)
def update_department(
    institution_id: int,
    department_id: int,
    payload: DepartmentUpdate,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.INSTITUTION_ADMIN and current_user.institution_id != institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit another institution's departments")

    department = db.get(Department, department_id)
    if department is None or department.institution_id != institution_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(department, field, value)
    db.commit()
    db.refresh(department)
    write_audit_log(db, current_user.user_id, "UPDATE", "department", department.department_id)
    return department


@router.delete("/{institution_id}/departments/{department_id}", status_code=204)
def delete_department(
    institution_id: int,
    department_id: int,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.INSTITUTION_ADMIN and current_user.institution_id != institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete another institution's departments")

    department = db.get(Department, department_id)
    if department is None or department.institution_id != institution_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    write_audit_log(db, current_user.user_id, "DELETE", "department", department_id)
    db.delete(department)
    db.commit()
    return None
