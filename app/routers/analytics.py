from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database.database import SessionLocal

from app.models.user import User
from app.models.research_paper import ResearchPaper
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
        "total_researchers": db.query(User).filter(User.role == "Researcher").count(),
        "total_institutions": db.query(Institution).count(),
        "total_collaborations": db.query(Collaboration).count(),
    }


@router.get("/top-researchers")
def top_researchers(db: Session = Depends(get_db)):

    results = (
        db.query(
            User.full_name,
            User.institution,
            func.count(ResearchPaper.id).label("total_publications")
        )
        .outerjoin(
            ResearchPaper,
            User.id == ResearchPaper.researcher_id
        )
        .filter(User.role == "Researcher")
        .group_by(
            User.id,
            User.full_name,
            User.institution
        )
        .order_by(desc("total_publications"))
        .limit(5)
        .all()
    )

    return [
        {
            "full_name": row.full_name,
            "institution": row.institution,
            "total_publications": row.total_publications
        }
        for row in results
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
            User.institution,
            func.count(User.id).label("researcher_count")
        )
        .filter(User.role == "Researcher")
        .group_by(User.institution)
        .order_by(desc("researcher_count"))
        .limit(5)
        .all()
    )

    return [
        {
            "institution": row.institution,
            "researchers": row.researcher_count
        }
        for row in results
    ]


@router.get("/collaboration-statistics")
def collaboration_statistics(db: Session = Depends(get_db)):

    total_researchers = (
        db.query(User)
        .filter(User.role == "Researcher")
        .count()
    )

    total_collaborations = db.query(Collaboration).count()

    total_publications = db.query(ResearchPaper).count()

    avg_publications = 0

    if total_researchers > 0:
        avg_publications = round(
            total_publications / total_researchers,
            2
        )

    return {
        "total_collaborations": total_collaborations,
        "average_publications_per_researcher": avg_publications,
        "total_researchers": total_researchers
    }
@router.get("/institution-report")
def institution_report(db: Session = Depends(get_db)):

    results = (
        db.query(
            User.institution,
            func.count(User.id).label("researchers")
        )
        .filter(
            User.institution != None,
            User.institution != ""
        )
        .group_by(User.institution)
        .order_by(desc("researchers"))
        .all()
    )

    return [
        {
            "institution": row.institution,
            "researchers": row.researchers
        }
        for row in results
    ]
@router.get("/collaboration-report")
def collaboration_report(db: Session = Depends(get_db)):

    pending = (
        db.query(Collaboration)
        .filter(Collaboration.status == "Pending")
        .count()
    )

    accepted = (
        db.query(Collaboration)
        .filter(Collaboration.status == "Accepted")
        .count()
    )

    rejected = (
        db.query(Collaboration)
        .filter(Collaboration.status == "Rejected")
        .count()
    )

    total = pending + accepted + rejected

    return {
        "total": total,
        "Pending": pending,
        "Accepted": accepted,
        "Rejected": rejected
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

    progress = 0

    if total_tasks > 0:
        progress = round(
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
        "project_progress": progress
    }
@router.get("/publication-status-report")
def publication_status_report(db: Session = Depends(get_db)):

    papers = db.query(ResearchPaper).all()

    report = {}

    for paper in papers:

        year = paper.publication_year

        if year not in report:

            report[year] = {
                "publication_year": year,
                "Published": 0,
                "Submitted": 0,
                "Draft": 0,
                "Archived": 0
            }

        status = paper.status

        if status in report[year]:
            report[year][status] += 1

    return list(report.values())