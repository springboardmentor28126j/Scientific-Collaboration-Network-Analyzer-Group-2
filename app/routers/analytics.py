from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database.database import SessionLocal
from app.models.research_paper import ResearchPaper
from app.models.researcher import Researcher
from app.models.institution import Institution
from app.models.collaboration import Collaboration
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.project_milestone import ProjectMilestone
from app.models.project_task import ProjectTask

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard")
def dashboard_summary(db: Session = Depends(get_db)):
    return {
        "total_papers": db.query(ResearchPaper).count(),
        "total_researchers": db.query(Researcher).count(),
        "total_institutions": db.query(Institution).count(),
        "total_collaborations": db.query(Collaboration).count(),
    }


@router.get("/top-researchers")
def top_researchers(db: Session = Depends(get_db)):

    researchers = (
        db.query(Researcher)
        .order_by(desc(Researcher.total_publications))
        .limit(5)
        .all()
    )

    return [
        {
            "full_name": researcher.full_name,
            "institution": researcher.institution,
            "total_publications": researcher.total_publications,
            "h_index": researcher.h_index
        }
        for researcher in researchers
    ]


@router.get("/publications-by-year")
def publications_by_year(db: Session = Depends(get_db)):

    results = (
        db.query(
            ResearchPaper.publication_year,
            func.count(ResearchPaper.id).label("count")
        )
        .group_by(ResearchPaper.publication_year)
        .order_by(ResearchPaper.publication_year)
        .all()
    )

    return [
        {
            "publication_year": year,
            "count": count
        }
        for year, count in results
    ]


@router.get("/top-institutions")
def top_institutions(db: Session = Depends(get_db)):

    results = (
        db.query(
            Researcher.institution,
            func.count(Researcher.id).label("researcher_count")
        )
        .group_by(Researcher.institution)
        .order_by(desc("researcher_count"))
        .limit(5)
        .all()
    )

    return [
        {
            "institution": institution,
            "researchers": researcher_count
        }
        for institution, researcher_count in results
    ]


@router.get("/collaboration-statistics")
def collaboration_statistics(db: Session = Depends(get_db)):

    total_researchers = db.query(Researcher).count()

    total_collaborations = db.query(Collaboration).count()

    average_publications = (
        db.query(func.avg(Researcher.total_publications)).scalar() or 0
    )

    average_h_index = (
        db.query(func.avg(Researcher.h_index)).scalar() or 0
    )

    return {
        "total_collaborations": total_collaborations,
        "average_publications_per_researcher": round(
            average_publications, 2
        ),
        "average_h_index": round(
            average_h_index, 2
        ),
        "total_researchers": total_researchers
    }


@router.get("/project-dashboard")
def project_dashboard(db: Session = Depends(get_db)):

    total_projects = db.query(Project).count()

    active_projects = (
        db.query(Project)
        .filter(Project.status == "Active")
        .count()
    )

    completed_projects = (
        db.query(Project)
        .filter(Project.status == "Completed")
        .count()
    )

    total_members = db.query(ProjectMember).count()

    total_milestones = db.query(ProjectMilestone).count()

    total_tasks = db.query(ProjectTask).count()

    completed_tasks = (
        db.query(ProjectTask)
        .filter(ProjectTask.status == "Completed")
        .count()
    )

    pending_tasks = (
        db.query(ProjectTask)
        .filter(ProjectTask.status == "Pending")
        .count()
    )

    project_progress = 0

    if total_tasks > 0:
        project_progress = round(
            (completed_tasks / total_tasks) * 100,
            2
        )

    return {

        "total_projects": total_projects,

        "active_projects": active_projects,

        "completed_projects": completed_projects,

        "total_members": total_members,

        "total_milestones": total_milestones,

        "total_tasks": total_tasks,

        "completed_tasks": completed_tasks,

        "pending_tasks": pending_tasks,

        "project_progress": project_progress

    }