from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.collaboration import Collaboration
from app.models.researcher import Researcher
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.institution import Institution

router = APIRouter(
    prefix="/network",
    tags=["Collaboration Network"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def collaboration_network(db: Session = Depends(get_db)):

    nodes = []
    edges = []

    researchers = db.query(Researcher).all()
    institutions = db.query(Institution).all()
    projects = db.query(Project).all()
    collaborations = db.query(Collaboration).all()
    project_members = db.query(ProjectMember).all()

    # -------------------------------
    # Institution Nodes
    # -------------------------------
    for institution in institutions:

        nodes.append({
            "id": f"I{institution.id}",
            "label": institution.institution_name,
            "type": "institution"
        })

    # -------------------------------
    # Researcher Nodes
    # -------------------------------
    for researcher in researchers:

        nodes.append({
            "id": f"R{researcher.id}",
            "label": researcher.full_name,
            "type": "researcher"
        })

        # Institution → Researcher
        institution = (
            db.query(Institution)
            .filter(
                Institution.institution_name == researcher.institution
            )
            .first()
        )

        if institution:

            edges.append({
                "source": f"I{institution.id}",
                "target": f"R{researcher.id}",
                "label": "Works At"
            })

    # -------------------------------
    # Project Nodes
    # -------------------------------
    for project in projects:

        nodes.append({
            "id": f"P{project.id}",
            "label": project.title,
            "type": "project"
        })

    # -------------------------------
    # Researcher → Project
    # -------------------------------
    for member in project_members:

        edges.append({
            "source": f"R{member.researcher_id}",
            "target": f"P{member.project_id}",
            "label": member.role
        })

    # -------------------------------
    # Researcher ↔ Researcher
    # -------------------------------
    for collaboration in collaborations:

        if collaboration.researcher_1_id != collaboration.researcher_2_id:

            edges.append({
                "source": f"R{collaboration.researcher_1_id}",
                "target": f"R{collaboration.researcher_2_id}",
                "label": "Collaborated"
            })

    return {
        "nodes": nodes,
        "edges": edges
    }