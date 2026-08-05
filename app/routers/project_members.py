from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app import models, schemas, crud
from app.oauth2 import get_current_user
from app.models import User

router = APIRouter(
    prefix="/project-members",
    tags=["Project Members"]
)


# ==========================
# Assign Researcher to Project
# ==========================

@router.post(
    "/",
    response_model=schemas.ProjectMemberResponse
)
def assign_researcher(
    member: schemas.ProjectMemberCreate,
    db: Session = Depends(get_db)
):

    return crud.create_project_member(
        db,
        member
    )



# ==========================
# Get Project Team
# ==========================

@router.get(
    "/project/{project_id}",
    response_model=list[schemas.ProjectMemberResponse]
)
def get_team_members(
    project_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_project_members(
        db,
        project_id
    )

# ---------------- Get All Project Members ----------------
@router.get("/")
def get_all_project_members(

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    return db.query(
        models.ProjectMember
    ).all()

# ==========================
# Remove Researcher
# ==========================

@router.delete("/{member_id}")
def remove_researcher(
    member_id: int,
    db: Session = Depends(get_db)
):

    member = crud.delete_project_member(
        db,
        member_id
    )


    if not member:

        raise HTTPException(
            status_code=404,
            detail="Member not found"
        )


    return {
        "message": "Researcher removed from project"
    }