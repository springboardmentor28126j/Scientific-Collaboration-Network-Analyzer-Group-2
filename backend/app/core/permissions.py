from fastapi import Depends, HTTPException
from app.models.user import UserRole

def require_role(*allowed_roles: UserRole):
    def role_checker(current_user_role: UserRole):
        if current_user_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return True
    return role_checker
