from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.oauth2 import get_current_user


router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)


# =========================================================
# GET AUDIT LOGS
# =========================================================

@router.get("/logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    # Only System Admin can view complete audit history
    if current_user.role != "system_admin":
        raise HTTPException(
            status_code=403,
            detail="Only system administrators can view audit logs"
        )

    logs = (
        db.query(models.ActivityLog)
        .order_by(
            models.ActivityLog.created_at.desc()
        )
        .all()
    )

    return logs


# =========================================================
# CREATE AUDIT LOG
# =========================================================

def create_activity_log(
    db: Session,
    user_id: int,
    action: str,
    description: str
):

    activity = models.ActivityLog(
        user_id=user_id,
        action=action,
        description=description
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity