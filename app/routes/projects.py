from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas, auth
from app.database import get_db
from app.notification_service import notify_all_users
from app.permissions import current_user, require_roles, scoped_projects_query
from app.audit import record as record_audit

router = APIRouter(prefix="/projects", tags=["Projects"], dependencies=[Depends(auth.require_authenticated)])


def _project_or_404(db: Session, project_id: int):
    project = crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, manager: models.User = Depends(require_roles("admin", "system admin", "institution admin")), db: Session = Depends(get_db)):
    created = crud.create_project(db, project)
    record_audit(db, action="created", entity_type="project", entity_id=created.id, user_id=manager.id, details=created.title)
    notify_all_users(db, notification_type="project", title="New project created", message=f"{created.title} is now available in the research workspace.", link="pages/projects.html")
    return created


@router.get("/")
def get_projects(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    return scoped_projects_query(db, user).order_by(models.Project.id.desc()).all()


@router.get("/{project_id}")
def get_project(project_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    project = scoped_projects_query(db, user).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
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


@router.put("/{project_id}")
def update_project(project_id: int, payload: schemas.ProjectCreate, manager: models.User = Depends(require_roles("admin", "system admin", "institution admin")), db: Session = Depends(get_db)):
    project = _project_or_404(db, project_id)
    if manager.role.lower() == "institution admin" and project.institution_id != manager.institution_id:
        raise HTTPException(status_code=403, detail="You can update only your institution's projects")
    for field, value in payload.model_dump().items():
        setattr(project, field, value)
    db.commit(); db.refresh(project)
    record_audit(db, action="updated", entity_type="project", entity_id=project.id, user_id=manager.id, actor_role=manager.role, details=project.title)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, manager: models.User = Depends(require_roles("admin", "system admin", "institution admin")), db: Session = Depends(get_db)):
    project = _project_or_404(db, project_id)
    if manager.role.lower() == "institution admin" and project.institution_id != manager.institution_id:
        raise HTTPException(status_code=403, detail="You can delete only your institution's projects")
    title = project.title
    db.delete(project); db.commit()
    record_audit(db, action="deleted", entity_type="project", entity_id=project_id, user_id=manager.id, actor_role=manager.role, details=title)
    return {"message": "Project deleted"}


@router.post("/{project_id}/assignments", status_code=status.HTTP_201_CREATED)
def add_project_assignment(project_id: int, assignment: schemas.ProjectAssignmentCreate, manager: models.User = Depends(require_roles("admin", "system admin", "institution admin")), db: Session = Depends(get_db)):
    _project_or_404(db, project_id)
    if not crud.get_researcher_by_id(db, assignment.researcher_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Researcher not found")
    existing = db.query(models.ProjectAssignment).filter(
        models.ProjectAssignment.project_id == project_id,
        models.ProjectAssignment.researcher_id == assignment.researcher_id,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Researcher is already assigned to this project")
    created = crud.add_project_assignment(db, project_id, assignment)
    record_audit(db, action="assigned", entity_type="project", entity_id=project_id, user_id=manager.id, actor_role=manager.role, details=f"Researcher {assignment.researcher_id}: {assignment.role}")
    return created


@router.delete("/{project_id}/assignments/{researcher_id}")
def remove_project_assignment(project_id: int, researcher_id: int, manager: models.User = Depends(require_roles("admin", "system admin", "institution admin")), db: Session = Depends(get_db)):
    project = _project_or_404(db, project_id)
    if manager.role.lower() == "institution admin" and project.institution_id != manager.institution_id:
        raise HTTPException(status_code=403, detail="You can manage only your institution's projects")
    assignment = db.query(models.ProjectAssignment).filter(models.ProjectAssignment.project_id == project_id, models.ProjectAssignment.researcher_id == researcher_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Project assignment not found")
    db.delete(assignment); db.commit()
    record_audit(db, action="assignment_removed", entity_type="project", entity_id=project_id, user_id=manager.id, actor_role=manager.role, details=f"Researcher {researcher_id}")
    return {"message": "Researcher removed from project"}
