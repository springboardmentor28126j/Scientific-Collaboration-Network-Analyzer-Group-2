from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.conference import Conference
from app.models.institution import Institution, Department
from app.models.publication import Publication
from app.models.project import Project
from app.models.user import User, UserRole, AffiliationStatus
from app.models.institution_request import InstitutionRequest
from app.schemas.institution import (
    InstitutionCreate, InstitutionOut, InstitutionUpdate,
    DepartmentCreate, DepartmentUpdate, DepartmentOut, InstitutionStats,
)
from app.schemas.institution_request import InstitutionRequestCreate, InstitutionRequestOut
from app.utils.audit import write_audit_log

router = APIRouter(prefix="/institutions", tags=["Institutions"])


@router.get("/requests", response_model=list[InstitutionRequestOut])
def list_institution_requests(
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
):
    return list(db.scalars(select(InstitutionRequest).where(InstitutionRequest.status == "PENDING")).all())


@router.post("/requests", response_model=InstitutionRequestOut, status_code=201)
def create_institution_request(
    payload: InstitutionRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # requested_by_user_id always comes from the authenticated caller, never
    # the request body -- otherwise anyone could file a request "on behalf
    # of" an arbitrary user_id, and that user would be silently promoted to
    # Institution Admin when a System Admin approves it.
    request_row = InstitutionRequest(**payload.model_dump(), requested_by_user_id=current_user.user_id)
    db.add(request_row)
    db.commit()
    db.refresh(request_row)
    return request_row


@router.post("/requests/{request_id}/approve", response_model=InstitutionOut)
def approve_institution_request(
    request_id: int,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
):
    request_row = db.get(InstitutionRequest, request_id)
    if request_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution request not found")
    if request_row.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Institution request is not pending")

    institution = Institution(
        name=request_row.institution_name,
        type="university",
        country=None,
        address=request_row.address,
        email_domain=request_row.domain,
    )
    db.add(institution)
    db.flush()

    user = db.get(User, request_row.requested_by_user_id)
    if user is not None:
        user.institution_id = institution.institution_id
        user.role = UserRole.INSTITUTION_ADMIN
        user.affiliation_status = AffiliationStatus.APPROVED
        user.is_active = True

    request_row.status = "APPROVED"
    db.commit()
    db.refresh(institution)
    write_audit_log(db, current_user.user_id, "CREATE", "institution", institution.institution_id)
    return institution


@router.post("/requests/{request_id}/reject")
def reject_institution_request(
    request_id: int,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
):
    request_row = db.get(InstitutionRequest, request_id)
    if request_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution request not found")
    if request_row.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Institution request is not pending")

    request_row.status = "REJECTED"
    db.commit()
    write_audit_log(db, current_user.user_id, "UPDATE", "institution_request", request_row.request_id)
    return {"status": "rejected"}


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


@router.get("/{institution_id}/stats", response_model=InstitutionStats)
def get_institution_stats(
    institution_id: int,
    current_user: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.INSTITUTION_ADMIN)),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.INSTITUTION_ADMIN and current_user.institution_id != institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another institution's reports")

    institution = db.get(Institution, institution_id)
    if institution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    total_researchers = db.scalar(
        select(func.count()).select_from(User).where(
            User.institution_id == institution_id, User.role == UserRole.RESEARCHER
        )
    )
    total_departments = db.scalar(
        select(func.count()).select_from(Department).where(Department.institution_id == institution_id)
    )
    pending_affiliation_requests = db.scalar(
        select(func.count()).select_from(User).where(
            User.institution_id == institution_id,
            User.role == UserRole.RESEARCHER,
            User.affiliation_status == AffiliationStatus.PENDING,
        )
    )

    pub_rows = db.execute(
        select(Publication.status, func.count())
        .where(Publication.institution_id == institution_id)
        .group_by(Publication.status)
    ).all()
    publications_by_status = {status_.value: count for status_, count in pub_rows}

    conf_rows = db.execute(
        select(Conference.status, func.count())
        .where(Conference.organizing_institution_id == institution_id)
        .group_by(Conference.status)
    ).all()
    conferences_by_status = {status_.value: count for status_, count in conf_rows}

    proj_rows = db.execute(
        select(Project.status, func.count())
        .where(Project.institution_id == institution_id)
        .group_by(Project.status)
    ).all()
    projects_by_status = {status_.value: count for status_, count in proj_rows}

    return InstitutionStats(
        institution_id=institution_id,
        total_researchers=total_researchers,
        total_departments=total_departments,
        pending_affiliation_requests=pending_affiliation_requests,
        total_publications=sum(publications_by_status.values()),
        publications_by_status=publications_by_status,
        total_conferences=sum(conferences_by_status.values()),
        conferences_by_status=conferences_by_status,
        total_projects=sum(projects_by_status.values()),
        projects_by_status=projects_by_status,
    )


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
