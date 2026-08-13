from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, schemas, auth, models
from app.permissions import require_roles, require_system_admin
from app.database import get_db
from app.notification_service import notify_users
from app.audit import record as record_audit

router = APIRouter(prefix="/users", tags=["Users"])

ALLOWED_REQUESTED_ROLES = {"researcher": "Researcher", "institution admin": "Institution Admin", "publisher": "Publisher", "reviewer": "Reviewer"}


@router.get("/me")
def get_current_user(
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_id = auth.read_token_subject(token)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "id": user.id, "name": user.name, "email": user.email, "role": user.role,
        "account_status": user.account_status, "researcher_id": user.researcher_id,
        "institution_id": user.institution_id,
    }


@router.get("/me/workspace")
def get_my_workspace(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    """Return only the profile/institution explicitly assigned to this account."""
    user_id = auth.read_token_subject(token)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    researcher = db.query(models.Researcher).filter(models.Researcher.id == user.researcher_id).first() if user.researcher_id else None
    institution = db.query(models.Institution).filter(models.Institution.id == user.institution_id).first() if user.institution_id else None
    return {
        "user_id": user.id, "role": user.role,
        "researcher": {"id": researcher.id, "full_name": researcher.full_name, "department": researcher.department, "institution_id": researcher.institution_id} if researcher else None,
        "institution": {"id": institution.id, "name": institution.name} if institution else None,
    }

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    requested_role = ALLOWED_REQUESTED_ROLES.get(user.role.lower())
    if not requested_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Choose a valid account type")
    user.role = requested_role
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")
    try:
        created = crud.create_user(db=db, user=user)
        # Reuse an existing academic profile when its verified email matches.
        matching_researcher = db.query(models.Researcher).filter(models.Researcher.email == created.email).first()
        matching_institution = db.query(models.Institution).filter(models.Institution.contact_email == created.email).first()
        if matching_researcher:
            created.researcher_id = matching_researcher.id
        if matching_institution:
            created.institution_id = matching_institution.id
        if matching_researcher or matching_institution:
            db.commit()
        record_audit(db, action="registered", entity_type="user", entity_id=created.id, details=f"Requested role: {created.requested_role}")
        if created.account_status == "pending":
            administrators = db.query(models.User).filter(models.User.role.in_(["admin", "System Admin"])).all()
            notify_users(db, administrators, notification_type="approval", title="New account approval request", message=f"{created.name} requested {created.requested_role} access.", link="pages/admin-approvals.html")
        return {"id": created.id, "name": created.name, "email": created.email, "role": created.role, "requested_role": created.requested_role, "account_status": created.account_status, "message": "Account request submitted for approval" if created.account_status == "pending" else "Researcher account created"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to register user")

@router.post("/login")
def login(user: schemas.UserLogin, request: Request, db: Session = Depends(get_db)):

    db_user = crud.get_user_by_email(db, user.email)

    if not db_user or not auth.verify_password(user.password, db_user.password):
        record_audit(db, action="failed_login", entity_type="security", details=f"Failed sign-in for {user.email}", request=request)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if db_user.account_status == "pending":
        record_audit(db, action="blocked_login", entity_type="security", entity_id=db_user.id, user_id=db_user.id, actor_role=db_user.role, details="Pending approval", request=request)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Your {db_user.requested_role} account request is pending administrator approval")
    if db_user.account_status != "active":
        record_audit(db, action="blocked_login", entity_type="security", entity_id=db_user.id, user_id=db_user.id, actor_role=db_user.role, details=f"Account status: {db_user.account_status}", request=request)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Your account request was not approved. {db_user.rejection_reason or 'Contact a System Admin for more information.'}")

    record_audit(db, action="login", entity_type="security", entity_id=db_user.id, user_id=db_user.id, actor_role=db_user.role, details="Successful login", request=request)

    return {
        "message": "Login Successful",
        "user": db_user.name,
        "name": db_user.name,
        "role": db_user.role,
        "access_token": auth.create_access_token(str(db_user.id)),
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(request: Request, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == auth.read_token_subject(token)).first()
    if user:
        record_audit(db, action="logout", entity_type="security", entity_id=user.id, user_id=user.id, actor_role=user.role, details="User signed out", request=request)
    return {"message": "Logout recorded"}


@router.get("/pending")
def pending_accounts(_admin: models.User = Depends(require_system_admin), db: Session = Depends(get_db)):
    return [{"id": user.id, "name": user.name, "email": user.email, "requested_role": user.requested_role, "account_status": user.account_status} for user in db.query(models.User).filter(models.User.account_status == "pending").order_by(models.User.id.desc()).all()]


@router.get("/accounts")
def list_accounts(manager: models.User = Depends(require_roles("admin", "system admin", "institution admin", "publisher")), db: Session = Depends(get_db)):
    """Admin-only account directory for reviewing existing workspace links."""
    query = db.query(models.User)
    if manager.role.lower() not in {"admin", "system admin"}:
        query = query.filter(models.User.role.ilike("reviewer"), models.User.account_status == "active")
    users = query.order_by(models.User.name).all()
    return [{
        "id": user.id, "name": user.name, "email": user.email, "role": user.role,
        "account_status": user.account_status, "researcher_id": user.researcher_id,
        "researcher_name": user.researcher.full_name if user.researcher else None,
        "institution_id": user.institution_id,
        "institution_name": user.institution.name if user.institution else None,
    } for user in users]


@router.post("/{user_id}/approve")
def approve_account(user_id: int, approval: schemas.UserApproval, admin: models.User = Depends(require_system_admin), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    approved_role = ALLOWED_REQUESTED_ROLES.get(approval.approved_role.lower())
    if not user or not approved_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account approval")
    if approval.researcher_id and not db.query(models.Researcher).filter(models.Researcher.id == approval.researcher_id).first():
        raise HTTPException(status_code=404, detail="Selected researcher profile does not exist")
    if approval.institution_id and not db.query(models.Institution).filter(models.Institution.id == approval.institution_id).first():
        raise HTTPException(status_code=404, detail="Selected institution does not exist")
    if approved_role == "Researcher" and not approval.researcher_id:
        raise HTTPException(status_code=400, detail="Assign a researcher profile before approving a Researcher account")
    if approved_role == "Institution Admin" and not approval.institution_id:
        raise HTTPException(status_code=400, detail="Assign an institution before approving an Institution Admin account")
    user.role = approved_role
    user.requested_role = approved_role
    user.account_status = "active"
    user.researcher_id = approval.researcher_id
    user.institution_id = approval.institution_id
    user.rejection_reason = None
    db.commit()
    record_audit(db, action="approved", entity_type="user", entity_id=user.id, user_id=admin.id, details=f"Approved role: {user.role}")
    notify_users(db, [user], notification_type="approval", title="Account approved", message=f"Your {user.role} account has been approved. You can now sign in.", link="dashboard.html")
    return {"message": "Account approved", "user_id": user.id, "role": user.role}


@router.post("/{user_id}/reject")
def reject_account(user_id: int, rejection: schemas.UserRejection, admin: models.User = Depends(require_system_admin), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id, models.User.account_status == "pending").first()
    if not user:
        raise HTTPException(status_code=404, detail="Pending account request not found")
    user.account_status = "rejected"
    user.rejection_reason = rejection.reason.strip()
    db.commit()
    record_audit(db, action="rejected", entity_type="user", entity_id=user.id, user_id=admin.id, details=user.rejection_reason)
    notify_users(db, [user], notification_type="approval", title="Account request update", message=f"Your {user.requested_role} account request was not approved. Reason: {user.rejection_reason}", link="index.html")
    return {"message": "Account request rejected"}


@router.put("/{user_id}/assignment")
def update_account_assignment(user_id: int, assignment: schemas.UserAssignment, admin: models.User = Depends(require_system_admin), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if assignment.researcher_id and not db.query(models.Researcher).filter(models.Researcher.id == assignment.researcher_id).first():
        raise HTTPException(status_code=404, detail="Selected researcher profile does not exist")
    if assignment.institution_id and not db.query(models.Institution).filter(models.Institution.id == assignment.institution_id).first():
        raise HTTPException(status_code=404, detail="Selected institution does not exist")
    user.researcher_id, user.institution_id = assignment.researcher_id, assignment.institution_id
    db.commit()
    record_audit(db, action="workspace_assigned", entity_type="user", entity_id=user.id, user_id=admin.id, actor_role=admin.role)
    return {"message": "Account workspace assignment updated"}


@router.put("/{user_id}/status")
def update_account_status(user_id: int, payload: schemas.UserStatusChange, admin: models.User = Depends(require_system_admin), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    requested_status = payload.account_status.strip().lower()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if requested_status not in {"active", "suspended"}:
        raise HTTPException(status_code=400, detail="Account status must be active or suspended")
    if user.id == admin.id and requested_status != "active":
        raise HTTPException(status_code=400, detail="You cannot suspend your own administrator account")
    user.account_status = requested_status
    db.commit()
    record_audit(db, action=requested_status, entity_type="user", entity_id=user.id, user_id=admin.id, actor_role=admin.role, details=user.email)
    return {"message": f"Account {requested_status}", "account_status": requested_status}
