from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, auth, models
from app.database import get_db
from app.permissions import current_user, SYSTEM_ADMIN_ROLES

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(auth.require_authenticated)]
)

@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    return {
        "total_researchers": crud.count_researchers(db),
        "total_institutions": crud.count_institutions(db),
        "total_publications": crud.count_publications(db),
        "total_conferences": crud.get_conferences(db).__len__(),
        "total_collaborations": crud.count_collaborations(db),
        "total_citations": crud.count_citations(db),
        "total_projects": crud.count_projects(db),
    }


@router.get("/workspace")
def get_workspace_dashboard(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    """Role-aware summary used by non-admin dashboards.

    It is deliberately calculated from the account's explicit assignments,
    rather than showing the complete administrator dataset.
    """
    role = user.role.lower()
    if role in SYSTEM_ADMIN_ROLES:
        return get_dashboard(db)
    publications = db.query(models.Publication)
    researchers = db.query(models.Researcher)
    collaborations = db.query(models.Collaboration)
    projects = db.query(models.Project)
    conferences = db.query(models.ConferenceParticipation)
    citations = db.query(models.Citation)
    if role == "researcher":
        if not user.researcher_id:
            return {"total_researchers": 0, "total_institutions": 0, "total_publications": 0, "total_conferences": 0, "total_collaborations": 0, "total_citations": 0, "total_projects": 0, "needs_workspace_assignment": True}
        publication_ids = [item.id for item in db.query(models.Publication).filter(models.Publication.authors.any(models.Researcher.id == user.researcher_id)).all()]
        return {
            "total_researchers": 1, "total_institutions": 1 if user.institution_id else 0,
            "total_publications": len(publication_ids),
            "total_conferences": conferences.filter(models.ConferenceParticipation.researcher_id == user.researcher_id).count(),
            "total_collaborations": collaborations.filter((models.Collaboration.researcher1_id == user.researcher_id) | (models.Collaboration.researcher2_id == user.researcher_id), models.Collaboration.status == "accepted").count(),
            "total_citations": citations.filter((models.Citation.citing_publication_id.in_(publication_ids)) | (models.Citation.cited_publication_id.in_(publication_ids))).count() if publication_ids else 0,
            "total_projects": db.query(models.ProjectAssignment).filter(models.ProjectAssignment.researcher_id == user.researcher_id).count(),
        }
    if role == "institution admin":
        if not user.institution_id:
            return {"total_researchers": 0, "total_institutions": 0, "total_publications": 0, "total_conferences": 0, "total_collaborations": 0, "total_citations": 0, "total_projects": 0, "needs_workspace_assignment": True}
        researcher_ids = [item.id for item in researchers.filter(models.Researcher.institution_id == user.institution_id).all()]
        publication_ids = [item.id for item in publications.filter(models.Publication.institution_id == user.institution_id).all()]
        return {
            "total_researchers": len(researcher_ids), "total_institutions": 1, "total_publications": len(publication_ids),
            "total_conferences": conferences.filter(models.ConferenceParticipation.researcher_id.in_(researcher_ids)).count() if researcher_ids else 0,
            "total_collaborations": collaborations.filter((models.Collaboration.researcher1_id.in_(researcher_ids)) | (models.Collaboration.researcher2_id.in_(researcher_ids)), models.Collaboration.status == "accepted").count() if researcher_ids else 0,
            "total_citations": citations.filter((models.Citation.citing_publication_id.in_(publication_ids)) | (models.Citation.cited_publication_id.in_(publication_ids))).count() if publication_ids else 0,
            "total_projects": projects.filter(models.Project.institution_id == user.institution_id).count(),
        }
    # Publisher and reviewer dashboards show workflow totals, but never user administration data.
    return {"total_researchers": 0, "total_institutions": 0, "total_publications": publications.count(), "total_conferences": 0, "total_collaborations": 0, "total_citations": citations.count(), "total_projects": 0}
