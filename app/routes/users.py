from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, schemas, auth, models
from app.database import get_db
from app.notification_service import notify_users
from app.audit import record as record_audit

router = APIRouter(prefix="/users", tags=["Users"])

ALLOWED_REQUESTED_ROLES = {"researcher": "Researcher", "institution admin": "Institution Admin", "publisher": "Publisher", "reviewer": "Reviewer"}


def _require_system_admin(token: str, db: Session) -> models.User:
    user_id = auth.read_token_subject(token)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.role.lower() not in {"admin", "system admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="System administrator access is required")
    return user


@router.get("/me")
def get_current_user(
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_id = auth.read_token_subject(token)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}

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
        record_audit(db, action="registered", entity_type="user", entity_id=created.id, details=f"Requested role: {created.requested_role}")
        if created.account_status == "pending":
            administrators = db.query(models.User).filter(models.User.role.in_(["admin", "System Admin"])).all()
            notify_users(db, administrators, notification_type="approval", title="New account approval request", message=f"{created.name} requested {created.requested_role} access.", link="pages/admin-approvals.html")
        return {"id": created.id, "name": created.name, "email": created.email, "role": created.role, "requested_role": created.requested_role, "account_status": created.account_status, "message": "Account request submitted for approval" if created.account_status == "pending" else "Researcher account created"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to register user")

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):

    db_user = crud.get_user_by_email(db, user.email)

    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if db_user.account_status == "pending":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Your {db_user.requested_role} account request is pending administrator approval")

    return {
        "message": "Login Successful",
        "user": db_user.name,
        "name": db_user.name,
        "role": db_user.role,
        "access_token": auth.create_access_token(str(db_user.id)),
        "token_type": "bearer"
    }


@router.get("/pending")
def pending_accounts(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    _require_system_admin(token, db)
    return [{"id": user.id, "name": user.name, "email": user.email, "requested_role": user.requested_role, "account_status": user.account_status} for user in db.query(models.User).filter(models.User.account_status == "pending").order_by(models.User.id.desc()).all()]


@router.post("/{user_id}/approve")
def approve_account(user_id: int, approval: schemas.UserApproval, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    _require_system_admin(token, db)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    approved_role = ALLOWED_REQUESTED_ROLES.get(approval.approved_role.lower())
    if not user or not approved_role or approved_role == "Researcher":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account approval")
    user.role = approved_role
    user.requested_role = approved_role
    user.account_status = "active"
    db.commit()
    record_audit(db, action="approved", entity_type="user", entity_id=user.id, details=f"Approved role: {user.role}")
    notify_users(db, [user], notification_type="approval", title="Account approved", message=f"Your {user.role} account has been approved. You can now sign in.", link="dashboard.html")
    return {"message": "Account approved", "user_id": user.id, "role": user.role}
