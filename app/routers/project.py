from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, crud


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


# ==========================
# Create Project
# ==========================

@router.post("/", response_model=schemas.ProjectResponse)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db)
):

    return crud.create_project(db, project)



# ==========================
# Get All Projects
# ==========================

@router.get("/", response_model=list[schemas.ProjectResponse])
def get_projects(
    db: Session = Depends(get_db)
):

    return crud.get_projects(db)

# ==========================
# Get Projects By Institution
# ==========================

@router.get("/institution/{institution_id}", response_model=list[schemas.ProjectResponse])
def get_projects_by_institution(
    institution_id: int,
    db: Session = Depends(get_db)
):

    projects = crud.get_projects_by_institution(
        db,
        institution_id
    )

    return projects

# ==========================
# Get Projects By Researcher
# ==========================

@router.get(
    "/researcher/{researcher_id}",
    response_model=list[schemas.ResearcherCollaborationResponse]
)
def get_projects_by_researcher(
    researcher_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_projects_by_researcher(
        db,
        researcher_id
    )
    
# ==========================
# Get Single Project
# ==========================

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    project = crud.get_project(db, project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    if project.institution:
        project.institution_name = project.institution.name

    return project


# ==========================
# Update Project
# ==========================

@router.put("/{project_id}", response_model=schemas.ProjectResponse)
def update_project(
    project_id: int,
    project: schemas.ProjectUpdate,
    db: Session = Depends(get_db)
):

    updated_project = crud.update_project(
        db,
        project_id,
        project
    )


    if not updated_project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )


    return updated_project



# ==========================
# Delete Project
# ==========================

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    project = crud.delete_project(
        db,
        project_id
    )


    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )


    return {
        "message": "Project deleted successfully"
    }

