from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/projects", tags=["Projects"])


def _project_or_404(db: Session, project_id: int):
    project = crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db, project)


@router.get("/")
def get_projects(db: Session = Depends(get_db)):
    return crud.get_projects(db)


@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = _project_or_404(db, project_id)
    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "funding_agency": project.funding_agency,
        "status": project.status,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "institution_id": project.institution_id,
        "assignments": [
            {"researcher_id": item.researcher_id, "researcher_name": item.researcher.full_name, "role": item.role}
            for item in project.assignments
        ],
    }


@router.post("/{project_id}/assignments", status_code=status.HTTP_201_CREATED)
def add_project_assignment(project_id: int, assignment: schemas.ProjectAssignmentCreate, db: Session = Depends(get_db)):
    _project_or_404(db, project_id)
    if not crud.get_researcher_by_id(db, assignment.researcher_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Researcher not found")
    existing = db.query(models.ProjectAssignment).filter(
        models.ProjectAssignment.project_id == project_id,
        models.ProjectAssignment.researcher_id == assignment.researcher_id,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Researcher is already assigned to this project")
    return crud.add_project_assignment(db, project_id, assignment)
