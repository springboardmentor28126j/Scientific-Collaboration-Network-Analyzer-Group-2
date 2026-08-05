from sqlalchemy.orm import Session
from datetime import datetime

from app.models.research_paper import ResearchPaper
from app.models.researcher import Researcher

from app.schemas.research_paper import (
    ResearchPaperCreate,
    ResearchPaperUpdate
)
from app.schemas.researcher import ResearcherCreate
 
from app.models.institution import Institution
from app.schemas.institution import InstitutionCreate

from app.models.collaboration import Collaboration
from app.schemas.collaboration import CollaborationCreate

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password
from app.models.conferences import Conference
from app.models.citation import Citation
from app.schemas.citation import CitationCreate
from app.models.project_document import ProjectDocument

from app.schemas.project_document import (
    ProjectDocumentCreate,
    ProjectDocumentUpdate
)
from app.models.project_comment import ProjectComment

from app.schemas.project_comment import (
    ProjectCommentCreate,
    ProjectCommentUpdate
)
from app.models.notification import Notification

from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate
)
from app.models.collaboration_request import CollaborationRequest

from app.schemas.collaboration_request import (
    CollaborationRequestCreate,
    CollaborationRequestUpdate
)
from app.models.institution_collaboration_request import (
    InstitutionCollaborationRequest
)

from app.schemas.institution_collaboration_request import (
    InstitutionCollaborationRequestCreate,
    InstitutionCollaborationRequestUpdate
)
from app.models.project_timeline import ProjectTimeline

from app.schemas.project_timeline import (
    ProjectTimelineCreate,
    ProjectTimelineUpdate
)
# -----------------------------
# Research Papers CRUD
# -----------------------------

def get_all_papers(db: Session):
    return db.query(ResearchPaper).all()


def get_paper_by_id(db: Session, paper_id: int):
    return db.query(ResearchPaper).filter(
        ResearchPaper.id == paper_id
    ).first()


def create_paper(db: Session, paper: ResearchPaperCreate):
    new_paper = ResearchPaper(**paper.model_dump())
    db.add(new_paper)
    db.commit()
    db.refresh(new_paper)
    return new_paper
from sqlalchemy import func
from app.models.user import User
from app.models.research_paper import ResearchPaper


def get_top_researchers(db: Session):

    return (
        db.query(
            User.id,
            User.full_name,
            User.institution,
            func.count(ResearchPaper.id).label("paper_count")
        )
        .outerjoin(
            ResearchPaper,
            User.id == ResearchPaper.researcher_id
        )
        .group_by(
            User.id,
            User.full_name,
            User.institution
        )
        .order_by(
            func.count(ResearchPaper.id).desc()
        )
        .all()
    )

# -----------------------------
# Researchers CRUD
# -----------------------------

def get_all_researchers(db: Session):
    return db.query(Researcher).all()


def get_researcher_by_id(db: Session, researcher_id: int):
    return db.query(Researcher).filter(
        Researcher.id == researcher_id
    ).first()


def create_researcher(db: Session, researcher: ResearcherCreate):
    new_researcher = Researcher(**researcher.model_dump())
    db.add(new_researcher)
    db.commit()
    db.refresh(new_researcher)
    return new_researcher


# -----------------------------
# Institutions CRUD
# -----------------------------

def get_all_institutions(db: Session):
    return db.query(Institution).all()


def get_institution_by_id(db: Session, institution_id: int):
    return db.query(Institution).filter(
        Institution.id == institution_id
    ).first()


def create_institution(db: Session, institution: InstitutionCreate):
    new_institution = Institution(**institution.model_dump())
    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)
    return new_institution


# -----------------------------
# Collaborations CRUD
# -----------------------------

def get_all_collaborations(db: Session):
    return db.query(Collaboration).all()


def get_collaboration_by_id(db: Session, collaboration_id: int):
    return db.query(Collaboration).filter(
        Collaboration.id == collaboration_id
    ).first()


def create_collaboration(db: Session, collaboration: CollaborationCreate):
    new_collaboration = Collaboration(**collaboration.model_dump())
    db.add(new_collaboration)
    db.commit()
    db.refresh(new_collaboration)
    return new_collaboration


# -----------------------------
# Search APIs
# -----------------------------

def search_papers_by_title(db: Session, title: str):
    return (
        db.query(ResearchPaper)
        .filter(ResearchPaper.title.ilike(f"%{title}%"))
        .all()
    )
def search_researchers_by_name(db: Session, name: str):
    return (
        db.query(Researcher)
        .filter(Researcher.full_name.ilike(f"%{name}%"))
        .all()
    )
def search_researchers_by_specialization(db: Session, specialization: str):
    return (
        db.query(Researcher)
        .filter(
            Researcher.specialization.ilike(f"%{specialization}%")
        )
        .all()
    )
def search_institutions_by_country(db: Session, country: str):
    return (
        db.query(Institution)
        .filter(Institution.country.ilike(f"%{country}%"))
        .all()
    )
# -----------------------------
# User Authentication CRUD
# -----------------------------

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):

    new_user = User(

        # Basic Details
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),

        # Personal Details
        phone_number=user.phone_number,
        gender=user.gender,
        date_of_birth=user.date_of_birth,

        # Academic Details
        institution=user.institution,
        department=user.department,
        designation=user.designation,

        # Research Details
        specialization=user.specialization,
        research_interests=user.research_interests,

        # Location
        country=user.country,
        state=user.state,
        city=user.city,

        # Institution Details
        website=user.website,
        established_year=user.established_year,
        institution_type=user.institution_type,

        # Role
        role=user.role

    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ----------------------------------------
    # Automatically create Researcher Profile
    # ----------------------------------------

    if new_user.role.lower() == "researcher":

        existing = db.query(Researcher).filter(
            Researcher.email == new_user.email
        ).first()

        if not existing:

            researcher = Researcher(

                full_name=new_user.full_name,
                email=new_user.email,
                institution=new_user.institution,
                department=new_user.department,
                specialization=new_user.specialization,

                h_index=0,
                total_publications=0

            )

            db.add(researcher)
            db.commit()

    return new_user


def update_user(
    db: Session,
    db_user: User,
    user: UserUpdate
):

    update_data = user.model_dump(exclude_unset=True)

    for key, value in update_data.items():

        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return db_user
# -----------------------------
# Get Papers by Researcher
# -----------------------------
def get_my_papers(
    db: Session,
    researcher_id: int
):
    return (
        db.query(ResearchPaper)
        .filter(
            ResearchPaper.researcher_id == researcher_id
        )
        .all()
    )


# -----------------------------
# Update Paper
# -----------------------------
def update_paper(
    db: Session,
    db_paper: ResearchPaper,
    updated_paper: ResearchPaperUpdate
):

    update_data = updated_paper.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():

        setattr(
            db_paper,
            key,
            value
        )

    db.commit()

    db.refresh(db_paper)

    return db_paper


# -----------------------------
# Delete Paper
# -----------------------------
def delete_paper(
    db: Session,
    db_paper: ResearchPaper
):

    db.delete(db_paper)

    db.commit()

    return {
        "message": "Paper deleted successfully"
    }
# ============================
# Conference CRUD
# ============================

from app.models.conferences import Conference


def get_all_conferences(db):
    return db.query(Conference).all()


def get_conference_by_id(db, conference_id):
    return (
        db.query(Conference)
        .filter(Conference.id == conference_id)
        .first()
    )


def get_my_conferences(db, researcher_id):
    return (
        db.query(Conference)
        .filter(Conference.researcher_id == researcher_id)
        .all()
    )


def create_conference(db, conference):
    db.add(conference)
    db.commit()
    db.refresh(conference)
    return conference


def update_conference(db, db_conference, updated_data):

    data = updated_data.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(db_conference, key, value)

    db.commit()
    db.refresh(db_conference)

    return db_conference


def delete_conference(db, conference):

    db.delete(conference)
    db.commit()

    return {
        "message": "Conference deleted successfully"
    }
def get_dashboard_stats(db, researcher_id):

    papers = db.query(ResearchPaper).filter(
        ResearchPaper.researcher_id == researcher_id
    ).count()

    conferences = db.query(Conference).filter(
        Conference.researcher_id == researcher_id
    ).count()

    collaborations = 0

    return {

        "papers": papers,

        "conferences": conferences,

        "collaborations": collaborations

    }
# -----------------------------
# Collaboration Tracking
# -----------------------------

def get_my_collaborations(db: Session, researcher_id: int):

    return (
        db.query(Collaboration)
        .filter(
            (Collaboration.researcher_1_id == researcher_id) |
            (Collaboration.researcher_2_id == researcher_id)
        )
        .all()
    )


def accept_collaboration(db: Session, collaboration: Collaboration):

    collaboration.status = "Accepted"

    db.commit()

    db.refresh(collaboration)

    return collaboration


def reject_collaboration(db: Session, collaboration: Collaboration):

    collaboration.status = "Rejected"

    db.commit()

    db.refresh(collaboration)

    return collaboration
# ============================
# Citation CRUD
# ============================

def get_all_citations(db: Session):

    citations = db.query(Citation).all()

    result = []

    for citation in citations:

        paper = (
            db.query(ResearchPaper)
            .filter(
                ResearchPaper.id ==
                citation.paper_id
            )
            .first()
        )

        cited = (
            db.query(ResearchPaper)
            .filter(
                ResearchPaper.id ==
                citation.cited_paper_id
            )
            .first()
        )

        result.append({

            "id": citation.id,

            "paper_id": citation.paper_id,

            "paper_title":
                paper.title if paper else "Unknown",

            "cited_paper_id":
                citation.cited_paper_id,

            "cited_paper_title":
                cited.title if cited else "Unknown",

            "citation_year":
                citation.citation_year,

            "citation_count":
                citation.citation_count,

            "created_at":
                citation.created_at,

            "updated_at":
                citation.updated_at

        })

    return result


def get_citation_by_id(
    db: Session,
    citation_id: int
):

    return (
        db.query(Citation)
        .filter(
            Citation.id == citation_id
        )
        .first()
    )


def get_citations_by_paper(
    db: Session,
    paper_id: int
):

    return (
        db.query(Citation)
        .filter(
            Citation.paper_id == paper_id
        )
        .all()
    )


def create_citation(
    db: Session,
    citation: CitationCreate
):

    if citation.paper_id == citation.cited_paper_id:

        raise Exception(
            "A paper cannot cite itself."
        )

    existing = (
        db.query(Citation)
        .filter(
            Citation.paper_id ==
            citation.paper_id,
            Citation.cited_paper_id ==
            citation.cited_paper_id
        )
        .first()
    )

    if existing:

        existing.citation_count += 1

        db.commit()

        db.refresh(existing)

        return {

            "id": existing.id,

            "paper_id": existing.paper_id,

            "paper_title":
                db.query(ResearchPaper)
                .filter(
                    ResearchPaper.id ==
                    existing.paper_id
                )
                .first()
                .title,

            "cited_paper_id":
                existing.cited_paper_id,

            "cited_paper_title":
                db.query(ResearchPaper)
                .filter(
                    ResearchPaper.id ==
                    existing.cited_paper_id
                )
                .first()
                .title,

            "citation_year":
                existing.citation_year,

            "citation_count":
                existing.citation_count,

            "created_at":
                existing.created_at,

            "updated_at":
                existing.updated_at

        }

    new_citation = Citation(
        **citation.model_dump()
    )

    db.add(new_citation)

    db.commit()

    db.refresh(new_citation)

    paper = (
        db.query(ResearchPaper)
        .filter(
            ResearchPaper.id ==
            new_citation.paper_id
        )
        .first()
    )

    cited = (
        db.query(ResearchPaper)
        .filter(
            ResearchPaper.id ==
            new_citation.cited_paper_id
        )
        .first()
    )

    return {

        "id": new_citation.id,

        "paper_id":
            new_citation.paper_id,

        "paper_title":
            paper.title if paper else "Unknown",

        "cited_paper_id":
            new_citation.cited_paper_id,

        "cited_paper_title":
            cited.title if cited else "Unknown",

        "citation_year":
            new_citation.citation_year,

        "citation_count":
            new_citation.citation_count,

        "created_at":
            new_citation.created_at,

        "updated_at":
            new_citation.updated_at

    }


def delete_citation(
    db: Session,
    citation: Citation
):

    db.delete(citation)

    db.commit()

    return {

        "message":
            "Citation deleted successfully"

    }
# ============================
# Project CRUD
# ============================

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_all_projects(db: Session):

    return db.query(Project).all()


def get_project_by_id(
    db: Session,
    project_id: int
):

    return (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )


def create_project(
    db: Session,
    project: ProjectCreate
):

    new_project = Project(
        **project.model_dump()
    )

    db.add(new_project)

    db.commit()

    db.refresh(new_project)

    return new_project


def update_project(
    db: Session,
    db_project: Project,
    updated_project: ProjectUpdate
):

    update_data = updated_project.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():

        setattr(
            db_project,
            key,
            value
        )

    db.commit()

    db.refresh(db_project)

    return db_project


def delete_project(
    db: Session,
    db_project: Project
):

    db.delete(db_project)

    db.commit()

    return {
        "message": "Project deleted successfully"
    }
# ============================
# Project Members CRUD
# ============================

from app.models.project_member import ProjectMember
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberUpdate
)


def get_all_project_members(db: Session):

    return db.query(ProjectMember).all()


def get_project_member_by_id(
    db: Session,
    member_id: int
):

    return (
        db.query(ProjectMember)
        .filter(ProjectMember.id == member_id)
        .first()
    )


def get_members_by_project(
    db: Session,
    project_id: int
):

    return (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id)
        .all()
    )


def create_project_member(
    db: Session,
    member: ProjectMemberCreate
):

    new_member = ProjectMember(
        **member.model_dump()
    )

    db.add(new_member)

    db.commit()

    db.refresh(new_member)

    return new_member


def update_project_member(
    db: Session,
    db_member: ProjectMember,
    updated_member: ProjectMemberUpdate
):

    update_data = updated_member.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():

        setattr(
            db_member,
            key,
            value
        )

    db.commit()

    db.refresh(db_member)

    return db_member


def delete_project_member(
    db: Session,
    db_member: ProjectMember
):

    db.delete(db_member)

    db.commit()

    return {
        "message": "Project member removed successfully"
    }
# ============================
# Project Milestones CRUD
# ============================

from app.models.project_milestone import ProjectMilestone
from app.schemas.project_milestone import (
    ProjectMilestoneCreate,
    ProjectMilestoneUpdate
)


def get_all_project_milestones(db: Session):

    return db.query(ProjectMilestone).all()


def get_project_milestone_by_id(
    db: Session,
    milestone_id: int
):

    return (
        db.query(ProjectMilestone)
        .filter(ProjectMilestone.id == milestone_id)
        .first()
    )


def get_milestones_by_project(
    db: Session,
    project_id: int
):

    return (
        db.query(ProjectMilestone)
        .filter(ProjectMilestone.project_id == project_id)
        .all()
    )


def create_project_milestone(
    db: Session,
    milestone: ProjectMilestoneCreate
):

    new_milestone = ProjectMilestone(
        **milestone.model_dump()
    )

    db.add(new_milestone)

    db.commit()

    db.refresh(new_milestone)

    return new_milestone


def update_project_milestone(
    db: Session,
    db_milestone: ProjectMilestone,
    updated_milestone: ProjectMilestoneUpdate
):

    update_data = updated_milestone.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():

        setattr(
            db_milestone,
            key,
            value
        )

    db.commit()

    db.refresh(db_milestone)

    return db_milestone


def delete_project_milestone(
    db: Session,
    db_milestone: ProjectMilestone
):

    db.delete(db_milestone)

    db.commit()

    return {
        "message": "Project milestone deleted successfully"
    }
# ============================
# Project Tasks CRUD
# ============================

from app.models.project_task import ProjectTask
from app.schemas.project_task import (
    ProjectTaskCreate,
    ProjectTaskUpdate
)


def get_all_project_tasks(db: Session):

    return db.query(ProjectTask).all()


def get_project_task_by_id(
    db: Session,
    task_id: int
):

    return (
        db.query(ProjectTask)
        .filter(ProjectTask.id == task_id)
        .first()
    )


def get_tasks_by_project(
    db: Session,
    project_id: int
):

    return (
        db.query(ProjectTask)
        .filter(ProjectTask.project_id == project_id)
        .all()
    )


def get_tasks_by_member(
    db: Session,
    researcher_id: int
):

    return (
        db.query(ProjectTask)
        .filter(ProjectTask.assigned_to == researcher_id)
        .all()
    )


def create_project_task(
    db: Session,
    task: ProjectTaskCreate
):

    new_task = ProjectTask(
        **task.model_dump()
    )

    db.add(new_task)

    db.commit()

    db.refresh(new_task)

    return new_task


def update_project_task(
    db: Session,
    db_task: ProjectTask,
    updated_task: ProjectTaskUpdate
):

    update_data = updated_task.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():

        setattr(
            db_task,
            key,
            value
        )

    db.commit()

    db.refresh(db_task)

    return db_task


def delete_project_task(
    db: Session,
    db_task: ProjectTask
):

    db.delete(db_task)

    db.commit()

    return {
        "message": "Project task deleted successfully"
    }
# ============================
# Activity Logs CRUD
# ============================

from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogCreate


def get_all_activity_logs(db: Session):

    return (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .all()
    )


def get_activity_log_by_id(
    db: Session,
    log_id: int
):

    return (
        db.query(ActivityLog)
        .filter(ActivityLog.id == log_id)
        .first()
    )


def get_logs_by_project(
    db: Session,
    project_id: int
):

    return (
        db.query(ActivityLog)
        .filter(ActivityLog.project_id == project_id)
        .order_by(ActivityLog.created_at.desc())
        .all()
    )


def get_logs_by_researcher(
    db: Session,
    researcher_id: int
):

    return (
        db.query(ActivityLog)
        .filter(ActivityLog.researcher_id == researcher_id)
        .order_by(ActivityLog.created_at.desc())
        .all()
    )


def create_activity_log(
    db: Session,
    log: ActivityLogCreate
):

    new_log = ActivityLog(
        **log.model_dump()
    )

    db.add(new_log)

    db.commit()

    db.refresh(new_log)

    return new_log


def delete_activity_log(
    db: Session,
    db_log: ActivityLog
):

    db.delete(db_log)

    db.commit()

    return {
        "message": "Activity log deleted successfully"
    }
# ===========================
# PROJECT DOCUMENT CRUD
# ===========================

def get_all_project_documents(db: Session):
    return db.query(ProjectDocument).all()


def get_project_documents_by_project(
    db: Session,
    project_id: int
):
    return (
        db.query(ProjectDocument)
        .filter(ProjectDocument.project_id == project_id)
        .all()
    )


def get_project_document_by_id(
    db: Session,
    document_id: int
):
    return (
        db.query(ProjectDocument)
        .filter(ProjectDocument.id == document_id)
        .first()
    )


def create_project_document(
    db: Session,
    document: ProjectDocumentCreate
):
    db_document = ProjectDocument(**document.model_dump())

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


def update_project_document(
    db: Session,
    db_document: ProjectDocument,
    document: ProjectDocumentUpdate
):
    update_data = document.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_document, key, value)

    db.commit()
    db.refresh(db_document)

    return db_document


def delete_project_document(
    db: Session,
    db_document: ProjectDocument
):
    db.delete(db_document)
    db.commit()

    return {
        "message": "Project document deleted successfully"
    }
# ===========================
# PROJECT COMMENT CRUD
# ===========================

def get_all_project_comments(db: Session):
    return db.query(ProjectComment).all()


def get_comments_by_project(
    db: Session,
    project_id: int
):
    return (
        db.query(ProjectComment)
        .filter(ProjectComment.project_id == project_id)
        .order_by(ProjectComment.created_at)
        .all()
    )


def get_project_comment_by_id(
    db: Session,
    comment_id: int
):
    return (
        db.query(ProjectComment)
        .filter(ProjectComment.id == comment_id)
        .first()
    )


def create_project_comment(
    db: Session,
    comment: ProjectCommentCreate
):
    db_comment = ProjectComment(**comment.model_dump())

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    return db_comment


def update_project_comment(
    db: Session,
    db_comment: ProjectComment,
    comment: ProjectCommentUpdate
):
    update_data = comment.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_comment, key, value)

    db.commit()
    db.refresh(db_comment)

    return db_comment


def delete_project_comment(
    db: Session,
    db_comment: ProjectComment
):
    db.delete(db_comment)
    db.commit()

    return {
        "message": "Project comment deleted successfully"
    }
# ===========================
# NOTIFICATION CRUD
# ===========================

def get_all_notifications(db: Session):
    return db.query(Notification).all()


def get_notifications_by_researcher(
    db: Session,
    researcher_id: int
):
    return (
        db.query(Notification)
        .filter(Notification.researcher_id == researcher_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


def get_notification_by_id(
    db: Session,
    notification_id: int
):
    return (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )


def create_notification(
    db: Session,
    notification: NotificationCreate
):
    db_notification = Notification(
        **notification.model_dump()
    )

    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    return db_notification


def update_notification(
    db: Session,
    db_notification: Notification,
    notification: NotificationUpdate
):
    update_data = notification.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(db_notification, key, value)

    db.commit()
    db.refresh(db_notification)

    return db_notification


def delete_notification(
    db: Session,
    db_notification: Notification
):
    db.delete(db_notification)
    db.commit()

    return {
        "message": "Notification deleted successfully"
    }
# ====================================
# COLLABORATION REQUEST CRUD
# ====================================
def get_all_collaboration_requests(db: Session):

    requests = (
        db.query(
            CollaborationRequest,
            Researcher.full_name.label("sender_name"),
            ResearchPaper.title.label("paper_title")
        )
        .join(
            Researcher,
            CollaborationRequest.sender_id == Researcher.id
        )
        .join(
            ResearchPaper,
            CollaborationRequest.paper_id == ResearchPaper.id
        )
        .all()
    )

    result = []

    for req, sender_name, paper_title in requests:

        receiver = (
            db.query(Researcher)
            .filter(
                Researcher.id == req.receiver_id
            )
            .first()
        )

        result.append({

            "id": req.id,

            "sender_id": req.sender_id,
            "receiver_id": req.receiver_id,

            "sender_name": sender_name,
            "receiver_name": receiver.full_name if receiver else "",

            "paper_id": req.paper_id,
            "paper_title": paper_title,

            "message": req.message,
            "status": req.status,
            "created_at": req.created_at

        })

    return result


def get_collaboration_request_by_id(
    db: Session,
    request_id: int
):
    return (
        db.query(CollaborationRequest)
        .filter(CollaborationRequest.id == request_id)
        .first()
    )


def get_requests_by_receiver(
    db: Session,
    receiver_id: int
):
    return (
        db.query(CollaborationRequest)
        .filter(
            CollaborationRequest.receiver_id == receiver_id
        )
        .all()
    )


def get_requests_by_sender(
    db: Session,
    sender_id: int
):
    return (
        db.query(CollaborationRequest)
        .filter(
            CollaborationRequest.sender_id == sender_id
        )
        .all()
    )

def create_collaboration_request(
    db: Session,
    request: CollaborationRequestCreate
):

    print("========== FUNCTION CALLED ==========")
    print(request)

    # Check duplicate pending request
    existing_request = (
        db.query(CollaborationRequest)
        .filter(
            CollaborationRequest.sender_id == request.sender_id,
            CollaborationRequest.receiver_id == request.receiver_id,
            CollaborationRequest.paper_id == request.paper_id,
            CollaborationRequest.status == "Pending"
        )
        .first()
    )

    if existing_request:
        print("Pending request already exists")
        return existing_request

    # Create Collaboration Request
    db_request = CollaborationRequest(

        sender_id=request.sender_id,
        receiver_id=request.receiver_id,
        paper_id=request.paper_id,
        message=request.message,
        status="Pending"

    )

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    print("Collaboration Request Created")

    # Create Notification
    try:

        notification = Notification(

            researcher_id=request.receiver_id,

            title="New Collaboration Request",

            message=f"Researcher #{request.sender_id} invited you to collaborate on Paper #{request.paper_id}.",

            is_read=False

        )

        db.add(notification)
        db.commit()

        print("Notification Saved")

    except Exception as e:

        db.rollback()
        print("Notification Error :", e)

    print("========== FUNCTION FINISHED ==========")

    return db_request
# ============================================
# INSTITUTION COLLABORATION REQUEST CRUD
# ============================================

def get_all_institution_requests(db: Session):

    return db.query(
        InstitutionCollaborationRequest
    ).all()


def get_institution_request_by_id(
    db: Session,
    request_id: int
):

    return (
        db.query(
            InstitutionCollaborationRequest
        )
        .filter(
            InstitutionCollaborationRequest.id == request_id
        )
        .first()
    )


def get_requests_by_receiver_institution(
    db: Session,
    institution_id: int
):

    return (
        db.query(
            InstitutionCollaborationRequest
        )
        .filter(
            InstitutionCollaborationRequest.receiver_institution_id == institution_id
        )
        .all()
    )


def get_requests_by_sender_institution(
    db: Session,
    institution_id: int
):

    return (
        db.query(
            InstitutionCollaborationRequest
        )
        .filter(
            InstitutionCollaborationRequest.sender_institution_id == institution_id
        )
        .all()
    )


def create_institution_request(
    db: Session,
    request: InstitutionCollaborationRequestCreate
):

    existing_request = (
        db.query(
            InstitutionCollaborationRequest
        )
        .filter(
            InstitutionCollaborationRequest.sender_institution_id
            == request.sender_institution_id,

            InstitutionCollaborationRequest.receiver_institution_id
            == request.receiver_institution_id,

            InstitutionCollaborationRequest.status == "Pending"
        )
        .first()
    )

    if existing_request:
        return existing_request

    db_request = InstitutionCollaborationRequest(
        **request.model_dump()
    )

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    return db_request


def update_institution_request(
    db: Session,
    db_request: InstitutionCollaborationRequest,
    request: InstitutionCollaborationRequestUpdate
):

    update_data = request.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(db_request, key, value)

    db.commit()
    db.refresh(db_request)

    return db_request


def delete_institution_request(
    db: Session,
    db_request: InstitutionCollaborationRequest
):

    db.delete(db_request)

    db.commit()

    return {
        "message": "Institution collaboration request deleted successfully"
    }
# ============================================
# PROJECT TIMELINE CRUD
# ============================================

def get_all_project_timelines(db: Session):

    return (
        db.query(ProjectTimeline)
        .order_by(ProjectTimeline.event_date)
        .all()
    )


def get_project_timeline_by_id(
    db: Session,
    timeline_id: int
):

    return (
        db.query(ProjectTimeline)
        .filter(
            ProjectTimeline.id == timeline_id
        )
        .first()
    )


def get_timelines_by_project(
    db: Session,
    project_id: int
):

    return (
        db.query(ProjectTimeline)
        .filter(
            ProjectTimeline.project_id == project_id
        )
        .order_by(ProjectTimeline.event_date)
        .all()
    )


def create_project_timeline(
    db: Session,
    timeline: ProjectTimelineCreate
):

    db_timeline = ProjectTimeline(
        **timeline.model_dump()
    )

    db.add(db_timeline)
    db.commit()
    db.refresh(db_timeline)

    return db_timeline


def update_project_timeline(
    db: Session,
    db_timeline: ProjectTimeline,
    timeline: ProjectTimelineUpdate
):

    update_data = timeline.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(db_timeline, key, value)

    db.commit()
    db.refresh(db_timeline)

    return db_timeline


def delete_project_timeline(
    db: Session,
    db_timeline: ProjectTimeline
):

    db.delete(db_timeline)
    db.commit()

    return {
        "message": "Project timeline deleted successfully"
    }
def update_collaboration_request(
    db: Session,
    db_request: CollaborationRequest,
    request: CollaborationRequestUpdate
):

    # Update status
    db_request.status = request.status

    db.commit()
    db.refresh(db_request)

    # -----------------------------------
    # ACCEPT REQUEST
    # -----------------------------------
    if db_request.status == "Accepted":

        existing = (
            db.query(Collaboration)
            .filter(
                Collaboration.researcher_1_id == db_request.sender_id,
                Collaboration.researcher_2_id == db_request.receiver_id,
                Collaboration.paper_id == db_request.paper_id
            )
            .first()
        )

        if existing is None:

            new_collaboration = Collaboration(

                researcher_1_id=db_request.sender_id,
                researcher_2_id=db_request.receiver_id,

                paper_id=db_request.paper_id,

                collaboration_year=datetime.now().year,

                status="Active",

                requested_by=db_request.sender_id

            )

            db.add(new_collaboration)

            notification = Notification(

                researcher_id=db_request.sender_id,

                title="Collaboration Accepted",

                message=f"Researcher #{db_request.receiver_id} accepted your collaboration request.",

                is_read=False

            )

            db.add(notification)

            db.commit()

            db.refresh(new_collaboration)

    # -----------------------------------
    # REJECT REQUEST
    # -----------------------------------
    elif db_request.status == "Rejected":

        notification = Notification(

            researcher_id=db_request.sender_id,

            title="Collaboration Rejected",

            message=f"Researcher #{db_request.receiver_id} rejected your collaboration request.",

            is_read=False

        )

        db.add(notification)

        db.commit()

    return db_request
def create_institution_collaboration_request(
    db: Session,
    request: InstitutionCollaborationRequestCreate
):

    db_request = InstitutionCollaborationRequest(
        **request.model_dump()
    )

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    sender = (
        db.query(Institution)
        .filter(
            Institution.id ==
            db_request.sender_institution_id
        )
        .first()
    )

    receiver = (
        db.query(Institution)
        .filter(
            Institution.id ==
            db_request.receiver_institution_id
        )
        .first()
    )

    return {

        "id": db_request.id,

        "sender_institution_id":
            db_request.sender_institution_id,

        "receiver_institution_id":
            db_request.receiver_institution_id,

        "sender_institution_name":
            sender.institution_name if sender else "Unknown",

        "receiver_institution_name":
            receiver.institution_name if receiver else "Unknown",

        "project_title":
            db_request.project_title,

        "purpose":
            db_request.purpose,

        "status":
            db_request.status,

        "created_at":
            db_request.created_at

    }
def get_all_institution_collaboration_requests(db: Session):

    requests = db.query(
        InstitutionCollaborationRequest
    ).all()

    result = []

    for req in requests:

        sender = (
            db.query(Institution)
            .filter(
                Institution.id == req.sender_institution_id
            )
            .first()
        )

        receiver = (
            db.query(Institution)
            .filter(
                Institution.id == req.receiver_institution_id
            )
            .first()
        )

        result.append({

            "id": req.id,

            "sender_institution_id":
                req.sender_institution_id,

            "receiver_institution_id":
                req.receiver_institution_id,

            # ✅ names should match schema
            "sender_institution_name":
                sender.institution_name if sender else "Unknown",

            "receiver_institution_name":
                receiver.institution_name if receiver else "Unknown",

            "project_title":
                req.project_title,

            "purpose":
                req.purpose,

            "status":
                req.status,

            "created_at":
                req.created_at

        })

    return result
def get_accepted_institution_collaboration_requests(db: Session):

    requests = (
        db.query(InstitutionCollaborationRequest)
        .filter(
            InstitutionCollaborationRequest.status == "Accepted"
        )
        .all()
    )

    result = []

    for req in requests:

        sender = (
            db.query(Institution)
            .filter(
                Institution.id == req.sender_institution_id
            )
            .first()
        )

        receiver = (
            db.query(Institution)
            .filter(
                Institution.id == req.receiver_institution_id
            )
            .first()
        )

        result.append({

            "id": req.id,

            "sender_institution_id":
                req.sender_institution_id,

            "receiver_institution_id":
                req.receiver_institution_id,

            "sender_institution_name":
                sender.institution_name if sender else "Unknown",

            "receiver_institution_name":
                receiver.institution_name if receiver else "Unknown",

            "project_title":
                req.project_title,

            "purpose":
                req.purpose,

            "status":
                req.status,

            "created_at":
                req.created_at

        })

    return result
def get_institution_collaboration_request_by_id(
    db: Session,
    request_id: int
):

    return (

        db.query(
            InstitutionCollaborationRequest
        )

        .filter(
            InstitutionCollaborationRequest.id ==
            request_id
        )

        .first()

    )
def update_institution_collaboration_request(
    db: Session,
    db_request: InstitutionCollaborationRequest,
    request: InstitutionCollaborationRequestUpdate
):

    db_request.status = request.status

    db.commit()
    db.refresh(db_request)

    return db_request