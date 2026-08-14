from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException
from app.models import Notification
from app.utils.pagination import get_pagination
from sqlalchemy import func
from app.routers.audit import create_activity_log
def create_researcher(
    db: Session,
    researcher: schemas.ResearcherCreate,
    user_id: int
):

    db_researcher = models.Researcher(
        user_id=user_id,
        full_name=researcher.full_name,
        email=researcher.email,
        department=researcher.department,
        institution=researcher.institution,
        designation=researcher.designation,
        research_interests=researcher.research_interests,
        skills=researcher.skills,
        phone=researcher.phone
    )

    db.add(db_researcher)
    db.commit()
    db.refresh(db_researcher)

    # =====================================
    # AUDIT LOG - CREATE
    # =====================================

    create_activity_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        description=f"Created researcher '{db_researcher.full_name}'"
    )

    # =====================================
    # RESEARCHER REGISTRATION NOTIFICATION
    # =====================================

    institution = db.query(models.Institution).filter(
        models.Institution.name == researcher.institution
    ).first()

    if institution:

        create_notification(
            db,
            schemas.NotificationCreate(

                receiver_id=institution.user_id,
                sender_id=user_id,
                title="New Researcher Registered",
                message=f'{researcher.full_name} has registered with your institution.',
                notification_type="researcher",
                reference_id=db_researcher.id,
                reference_type="researcher"

            )
        )

    # System Admin Notification

    system_admins = db.query(models.User).filter(
        models.User.role == "system_admin"
    ).all()

    for admin in system_admins:

        create_notification(
            db,
            schemas.NotificationCreate(

                receiver_id=admin.id,
                sender_id=user_id,
                title="New Researcher Registered",
                message=f'{researcher.full_name} has joined the research platform.',
                notification_type="researcher",
                reference_id=db_researcher.id,
                reference_type="researcher"

            )
        )

    return db_researcher

def get_all_researchers(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "name",
    order: str = "asc"
):
    query = db.query(models.Researcher)

    # -----------------------------
    # SORTING
    # -----------------------------

    if sort_by == "name":
        sort_column = func.lower(models.Researcher.full_name)
    else:
        sort_column = func.lower(models.Researcher.full_name)

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # -----------------------------
    # TOTAL RECORDS
    # -----------------------------

    total_records = query.count()

    # -----------------------------
    # PAGINATION
    # -----------------------------

    pagination = get_pagination(
        page,
        page_size,
        total_records
    )

    researchers = (
        query
        .offset(pagination["offset"])
        .limit(page_size)
        .all()
    )

    return researchers, pagination

def get_researcher_by_id(db: Session, researcher_id: int):
    return db.query(models.Researcher).filter(
        models.Researcher.id == researcher_id
    ).first()


def update_researcher(
    db: Session,
    researcher_id: int,
    researcher: schemas.ResearcherUpdate
):

    db_researcher = db.query(models.Researcher).filter(
        models.Researcher.id == researcher_id
    ).first()

    if not db_researcher:
        return None

    # Get update data
    update_data = researcher.model_dump(
        exclude_unset=True
    )

    # Update researcher table
    for key, value in update_data.items():
        setattr(
            db_researcher,
            key,
            value
        )

    # Update linked user table
    if db_researcher.user_id:

        db_user = db.query(models.User).filter(
            models.User.id == db_researcher.user_id
        ).first()

        if db_user:

            if "full_name" in update_data:
                db_user.full_name = update_data["full_name"]

            if "email" in update_data:
                db_user.email = update_data["email"]

    db.commit()
    db.refresh(db_researcher)

    # =====================================
    # AUDIT LOG - UPDATE
    # =====================================

    create_activity_log(
        db=db,
        user_id=db_researcher.user_id,
        action="UPDATE",
        description=f"Updated researcher '{db_researcher.full_name}'"
    )

    return db_researcher

def delete_researcher(
    db: Session,
    researcher_id: int
):

    db_researcher = db.query(models.Researcher).filter(
        models.Researcher.id == researcher_id
    ).first()

    if db_researcher:

        # Save details before deletion
        researcher_name = db_researcher.full_name
        user_id = db_researcher.user_id

        # Delete researcher
        db.delete(db_researcher)
        db.commit()

        # =====================================
        # AUDIT LOG - DELETE
        # =====================================

        create_activity_log(
            db=db,
            user_id=user_id,
            action="DELETE",
            description=f"Deleted researcher '{researcher_name}'"
        )

    return db_researcher
    
def create_publication(db: Session, publication: schemas.PublicationCreate):

    # DOI allowed only for Published publications
    if publication.doi and publication.status != "Published":
        raise HTTPException(
            status_code=400,
            detail="DOI can be added only for published publications"
        )

    publication_data = publication.model_dump()

    db_publication = models.Publication(**publication_data)

    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)

    # Get Researcher
    researcher = db.query(models.Researcher).filter(
        models.Researcher.id == db_publication.researcher_id
    ).first()

    # =====================================================
    # AUDIT LOG
    # =====================================================

    create_activity_log(
        db=db,
        user_id=researcher.user_id if researcher else None,
        action="CREATE",
        description=f"Created publication '{db_publication.title}'"
    )

    # =====================================================
    # ROLE-BASED NOTIFICATIONS
    # =====================================================

    if researcher:

        # Notification to Researcher
        create_notification(
            db,
            schemas.NotificationCreate(
                receiver_id=researcher.user_id,
                sender_id=researcher.user_id,
                title="Publication Added",
                message=f'Your publication "{db_publication.title}" has been added successfully.',
                notification_type="publication",
                reference_id=db_publication.id,
                reference_type="publication"
            )
        )

        # Notification to Institution Admin
        institution = db.query(models.Institution).filter(
            models.Institution.name == researcher.institution
        ).first()

        if institution:

            create_notification(
                db,
                schemas.NotificationCreate(
                    receiver_id=institution.user_id,
                    sender_id=researcher.user_id,
                    title="New Publication",
                    message=f'{researcher.full_name} added a new publication "{db_publication.title}".',
                    notification_type="publication",
                    reference_id=db_publication.id,
                    reference_type="publication"
                )
            )

        # Notification to System Admins
        system_admins = db.query(models.User).filter(
            models.User.role == "system_admin"
        ).all()

        for admin in system_admins:

            create_notification(
                db,
                schemas.NotificationCreate(
                    receiver_id=admin.id,
                    sender_id=researcher.user_id,
                    title="Publication Added",
                    message=f'{researcher.full_name} from {researcher.institution} added a new publication.',
                    notification_type="publication",
                    reference_id=db_publication.id,
                    reference_type="publication"
                )
            )

    return db_publication

def get_all_publications(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "year",
    order: str = "desc"
):
    query = db.query(models.Publication)

    # -----------------------------
    # SORTING
    # -----------------------------

    if sort_by == "title":
        sort_column = func.lower(models.Publication.title)

    else:
        sort_column = models.Publication.publication_year

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # -----------------------------
    # TOTAL RECORDS
    # -----------------------------

    total_records = query.count()

    # -----------------------------
    # PAGINATION
    # -----------------------------

    pagination = get_pagination(
        page,
        page_size,
        total_records
    )

    publications = (
        query
        .offset(pagination["offset"])
        .limit(page_size)
        .all()
    )

    return publications, pagination

def get_publication_by_id(db: Session, publication_id: int):
    return db.query(models.Publication).filter(
        models.Publication.id == publication_id
    ).first()


def update_publication(
    db: Session,
    publication_id: int,
    publication: schemas.PublicationUpdate
):

    db_publication = db.query(models.Publication).filter(
        models.Publication.id == publication_id
    ).first()

    if not db_publication:
        return None

    update_data = publication.model_dump(
        exclude_unset=True
    )

    # DOI validation
    if (
        "doi" in update_data
        and update_data["doi"]
        and update_data.get(
            "status",
            db_publication.status
        ) != "Published"
    ):
        raise HTTPException(
            status_code=400,
            detail="DOI can be added only for published publications"
        )

    # Update publication
    for key, value in update_data.items():
        setattr(
            db_publication,
            key,
            value
        )

    db.commit()
    db.refresh(db_publication)

    # =====================================================
    # AUDIT LOG
    # =====================================================

    researcher = db.query(models.Researcher).filter(
        models.Researcher.id == db_publication.researcher_id
    ).first()

    create_activity_log(
        db=db,
        user_id=researcher.user_id if researcher else None,
        action="UPDATE",
        description=f"Updated publication '{db_publication.title}'"
    )

    return db_publication

def delete_publication(
    db: Session,
    publication_id: int
):

    db_publication = db.query(models.Publication).filter(
        models.Publication.id == publication_id
    ).first()

    if db_publication:

        # Save details before deleting
        publication_title = db_publication.title

        researcher = db.query(models.Researcher).filter(
            models.Researcher.id == db_publication.researcher_id
        ).first()

        user_id = researcher.user_id if researcher else None

        # Delete publication
        db.delete(db_publication)
        db.commit()

        # =====================================================
        # AUDIT LOG
        # =====================================================

        create_activity_log(
            db=db,
            user_id=user_id,
            action="DELETE",
            description=f"Deleted publication '{publication_title}'"
        )

    return db_publication

def create_institution(
    db: Session,
    institution: schemas.InstitutionCreate
):
    db_institution = models.Institution(
        **institution.model_dump()
    )

    db.add(db_institution)
    db.commit()
    db.refresh(db_institution)

    # =====================================================
    # AUDIT LOG
    # =====================================================

    create_activity_log(
        db=db,
        user_id=db_institution.user_id,
        action="CREATE",
        description=f"Created institution '{db_institution.name}'"
    )

    return db_institution


def get_all_institutions(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "name",
    order: str = "asc"
):

    query = db.query(models.Institution)

    # -----------------------------
    # SORTING
    # -----------------------------

    if sort_by == "name":
        sort_column = func.lower(models.Institution.name)

    elif sort_by == "institution_type":
        sort_column = func.lower(models.Institution.institution_type)

    elif sort_by == "location":
        sort_column = func.lower(models.Institution.location)

    else:
        # Default sorting
        sort_column = func.lower(models.Institution.name)

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # -----------------------------
    # TOTAL RECORDS
    # -----------------------------

    total_records = query.count()

    # -----------------------------
    # PAGINATION
    # -----------------------------

    pagination = get_pagination(
        page,
        page_size,
        total_records
    )

    institutions = (
        query
        .offset(pagination["offset"])
        .limit(page_size)
        .all()
    )

    return institutions, pagination
def get_institution_by_id(db: Session, institution_id: int):
    return db.query(models.Institution).filter(
        models.Institution.id == institution_id
    ).first()


def update_institution(
    db: Session,
    institution_id: int,
    institution: schemas.InstitutionUpdate
):
    db_institution = db.query(models.Institution).filter(
        models.Institution.id == institution_id
    ).first()

    if db_institution:

        for key, value in institution.model_dump().items():
            setattr(db_institution, key, value)

        db.commit()
        db.refresh(db_institution)

        # =====================================================
        # AUDIT LOG
        # =====================================================

        create_activity_log(
            db=db,
            user_id=db_institution.user_id,
            action="UPDATE",
            description=f"Updated institution '{db_institution.name}'"
        )

    return db_institution


def delete_institution(
    db: Session,
    institution_id: int
):
    db_institution = db.query(models.Institution).filter(
        models.Institution.id == institution_id
    ).first()

    if db_institution:

        # Save details before deleting
        institution_name = db_institution.name
        user_id = db_institution.user_id

        db.delete(db_institution)
        db.commit()

        # =====================================================
        # AUDIT LOG
        # =====================================================

        create_activity_log(
            db=db,
            user_id=user_id,
            action="DELETE",
            description=f"Deleted institution '{institution_name}'"
        )

    return db_institution

def get_conferences_by_institution(
    db: Session,
    institution_name: str
):
    return db.query(models.Conference).filter(
        models.Conference.institution == institution_name
    ).all()
    
def create_conference(
    db: Session,
    conference: schemas.ConferenceCreate,
    creator_user_id: int,
    creator_role: str
):

    db_conference = models.Conference(
        **conference.model_dump()
    )

    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)

    # =====================================================
    # AUDIT LOG
    # =====================================================

    create_activity_log(
        db=db,
        user_id=creator_user_id,
        action="CREATE",
        description=f"Created conference '{db_conference.title}'"
    )

    # ==========================
    # CONFERENCE NOTIFICATIONS
    # ==========================

    # Get creator details

    creator = db.query(models.User).filter(
        models.User.id == creator_user_id
    ).first()

    # ---------------------------------
    # Notify Researchers
    # ---------------------------------

    researchers = db.query(models.Researcher).all()

    for researcher in researchers:

        create_notification(
            db,
            schemas.NotificationCreate(

                receiver_id=researcher.user_id,

                sender_id=creator_user_id,

                title="New Conference",

                message=f'A new conference "{db_conference.title}" has been created.',

                notification_type="conference",

                reference_id=db_conference.id,

                reference_type="conference"
            )
        )

    # ---------------------------------
    # If Institution Admin created
    # Notify System Admin
    # ---------------------------------

    if creator_role == "institution_admin":

        system_admins = db.query(models.User).filter(
            models.User.role == "system_admin"
        ).all()

        institution_name = db_conference.institution

        for admin in system_admins:

            create_notification(
                db,
                schemas.NotificationCreate(

                    receiver_id=admin.id,

                    sender_id=creator_user_id,

                    title="Conference Created",

                    message=f'A new conference "{db_conference.title}" has been created by {institution_name}.',

                    notification_type="conference",

                    reference_id=db_conference.id,

                    reference_type="conference"
                )
            )

    return db_conference

def get_all_conferences(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "date",
    order: str = "asc"
):

    query = db.query(models.Conference)

    # -----------------------------
    # SORTING
    # -----------------------------

    if sort_by == "title":
        sort_column = func.lower(models.Conference.title)

    elif sort_by == "date":
        sort_column = models.Conference.conference_date

    else:
        sort_column = models.Conference.conference_date

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # -----------------------------
    # TOTAL RECORDS
    # -----------------------------

    total_records = query.count()

    # -----------------------------
    # PAGINATION
    # -----------------------------

    pagination = get_pagination(
        page,
        page_size,
        total_records
    )

    conferences = (
        query
        .offset(pagination["offset"])
        .limit(page_size)
        .all()
    )

    return conferences, pagination

def get_conference_by_id(db: Session, conference_id: int):
    return db.query(models.Conference).filter(
        models.Conference.id == conference_id
    ).first()


def update_conference(
    db: Session,
    conference_id: int,
    conference: schemas.ConferenceUpdate
):

    db_conference = db.query(models.Conference).filter(
        models.Conference.id == conference_id
    ).first()

    if db_conference:

        update_data = conference.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():

            setattr(
                db_conference,
                key,
                value
            )

        db.commit()
        db.refresh(db_conference)

        # =====================================================
        # AUDIT LOG
        # =====================================================

        create_activity_log(
            db=db,
            user_id=db_conference.created_by,
            action="UPDATE",
            description=f"Updated conference '{db_conference.title}'"
        )

    return db_conference

def delete_conference(db: Session, conference_id: int):

    db_conference = db.query(models.Conference).filter(
        models.Conference.id == conference_id
    ).first()

    if db_conference:

        # Save details before deleting
        conference_title = db_conference.title
        user_id = db_conference.created_by

        db.delete(db_conference)
        db.commit()

        # =====================================================
        # AUDIT LOG
        # =====================================================

        create_activity_log(
            db=db,
            user_id=user_id,
            action="DELETE",
            description=f"Deleted conference '{conference_title}'"
        )

    return db_conference

# ---------------- Conference Registration CRUD ----------------


def create_conference_registration(
    db: Session,
    registration: schemas.ConferenceRegistrationCreate,
    researcher_id: int
):

    db_registration = models.ConferenceRegistration(

        researcher_id=researcher_id,

        conference_id=registration.conference_id,

        participation_type=registration.participation_type,

        presentation_title=registration.presentation_title,

        publication_id=registration.publication_id,

        presentation_mode=registration.presentation_mode
    )

    db.add(db_registration)

    db.commit()

    db.refresh(db_registration)

    # Get Researcher
    researcher = db.query(models.Researcher).filter(
        models.Researcher.id == researcher_id
    ).first()

    # Get Conference
    conference = db.query(models.Conference).filter(
        models.Conference.id == registration.conference_id
    ).first()

    # =====================================================
    # AUDIT LOG
    # =====================================================

    if researcher and conference:

        create_activity_log(
            db=db,
            user_id=researcher.user_id,
            action="CREATE",
            description=f"Registered for conference '{conference.title}'"
        )

    # ==========================
    # CONFERENCE REGISTRATION NOTIFICATIONS
    # ==========================

    if researcher and conference:

        # --------------------------
        # Researcher
        # --------------------------

        create_notification(
            db,
            schemas.NotificationCreate(

                receiver_id=researcher.user_id,

                sender_id=researcher.user_id,

                title="Conference Registration",

                message=f'You have successfully registered for "{conference.title}".',

                notification_type="conference",

                reference_id=conference.id,

                reference_type="conference"
            )
        )

        # --------------------------
        # Institution Admin
        # --------------------------

        institution = db.query(models.Institution).filter(
            models.Institution.name == researcher.institution
        ).first()

        if institution:

            create_notification(
                db,
                schemas.NotificationCreate(

                    receiver_id=institution.user_id,

                    sender_id=researcher.user_id,

                    title="Researcher Registered",

                    message=f'{researcher.full_name} registered for conference "{conference.title}".',

                    notification_type="conference",

                    reference_id=conference.id,

                    reference_type="conference"
                )
            )

        # --------------------------
        # System Admin
        # --------------------------

        system_admins = db.query(models.User).filter(
            models.User.role == "system_admin"
        ).all()

        for admin in system_admins:

            create_notification(
                db,
                schemas.NotificationCreate(

                    receiver_id=admin.id,

                    sender_id=researcher.user_id,

                    title="Conference Registration",

                    message=f'{researcher.full_name} registered for conference "{conference.title}".',

                    notification_type="conference",

                    reference_id=conference.id,

                    reference_type="conference"
                )
            )

    return db_registration

def get_registrations_by_researcher(
    db: Session,
    researcher_id: int
):

    registrations = db.query(
        models.ConferenceRegistration
    ).filter(
        models.ConferenceRegistration.researcher_id == researcher_id
    ).all()


    result = []


    for registration in registrations:

        result.append({

            "id": registration.id,

            "researcher_id": registration.researcher_id,

            "researcher_name": registration.researcher.full_name
            if registration.researcher
            else None,

            "conference_id": registration.conference_id,

            "conference_title": registration.conference.title
            if registration.conference
            else None,

            "participation_type": registration.participation_type,

            "presentation_title": registration.presentation_title,

            "publication_id": registration.publication_id,

            "presentation_mode": registration.presentation_mode,

            "status": registration.status,

            "registration_date": registration.registration_date

        })


    return result





def get_conference_participants(
    db: Session,
    conference_id: int
):

    registrations = db.query(
        models.ConferenceRegistration
    ).filter(
        models.ConferenceRegistration.conference_id == conference_id
    ).all()


    result = []


    for registration in registrations:

        result.append({

            "id": registration.id,

            "researcher_id": registration.researcher_id,

            "researcher_name": registration.researcher.full_name
            if registration.researcher
            else None,

            "conference_id": registration.conference_id,

            "conference_title": registration.conference.title
            if registration.conference
            else None,

            "participation_type": registration.participation_type,

            "presentation_title": registration.presentation_title,

            "publication_id": registration.publication_id,

            "presentation_mode": registration.presentation_mode,

            "status": registration.status,

            "registration_date": registration.registration_date

        })


    return result
    
def delete_conference_registration(
    db: Session,
    registration_id: int
):

    registration = db.query(
        models.ConferenceRegistration
    ).filter(
        models.ConferenceRegistration.id == registration_id
    ).first()

    if registration:

        # Get researcher
        researcher = db.query(models.Researcher).filter(
            models.Researcher.id == registration.researcher_id
        ).first()

        # Get conference
        conference = db.query(models.Conference).filter(
            models.Conference.id == registration.conference_id
        ).first()

        user_id = researcher.user_id if researcher else None
        conference_title = conference.title if conference else "Unknown Conference"

        # Delete registration
        db.delete(registration)
        db.commit()

        # =====================================================
        # AUDIT LOG
        # =====================================================

        create_activity_log(
            db=db,
            user_id=user_id,
            action="DELETE",
            description=f"Cancelled conference registration for '{conference_title}'"
        )

    return registration
# ==========================
# Project CRUD Operations
# ==========================

from . import models, schemas


def create_project(db, project):

    db_project = models.Project(
        project_name=project.project_name,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        status=project.status,
        institution_id=project.institution_id
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # ==========================================
    # AUDIT LOG
    # ==========================================

    institution = db.query(models.Institution).filter(
        models.Institution.id == db_project.institution_id
    ).first()

    if institution:
        create_activity_log(
            db=db,
            user_id=institution.user_id,
            action="CREATE",
            description=f"Created project '{db_project.project_name}'"
        )

    # ==========================================
    # PROJECT CREATED NOTIFICATIONS
    # ==========================================

    # Institution Admin Notification

    if institution:

        create_notification(
            db,
            schemas.NotificationCreate(

                receiver_id=institution.user_id,

                sender_id=institution.user_id,

                title="Project Created",

                message=f'Your project "{db_project.project_name}" has been created successfully.',

                notification_type="project",

                reference_id=db_project.id,

                reference_type="project"
            )
        )

    # System Admin Notification

    system_admins = db.query(models.User).filter(
        models.User.role == "system_admin"
    ).all()

    for admin in system_admins:

        create_notification(
            db,
            schemas.NotificationCreate(

                receiver_id=admin.id,

                sender_id=institution.user_id if institution else None,

                title="New Project Created",

                message=f'A new project "{db_project.project_name}" has been created for {institution.name if institution else "an institution"}.',

                notification_type="project",

                reference_id=db_project.id,

                reference_type="project"
            )
        )

    return db_project


def get_projects(
    db,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "project_name",
    order: str = "asc"
):

    query = db.query(models.Project)

    # -----------------------------
    # SORTING
    # -----------------------------

    if sort_by == "project_name":
        sort_column = func.lower(models.Project.project_name)

    elif sort_by == "status":
        sort_column = func.lower(models.Project.status)

    elif sort_by == "start_date":
        sort_column = models.Project.start_date

    else:
        sort_column = func.lower(models.Project.project_name)

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # -----------------------------
    # TOTAL RECORDS
    # -----------------------------

    total_records = query.count()

    # -----------------------------
    # PAGINATION
    # -----------------------------

    pagination = get_pagination(
        page,
        page_size,
        total_records
    )

    projects = (
        query
        .offset(pagination["offset"])
        .limit(page_size)
        .all()
    )

    # -----------------------------
    # INSTITUTION NAME
    # -----------------------------

    for project in projects:

        if project.institution:
            project.institution_name = project.institution.name
        else:
            project.institution_name = None

    return projects, pagination

def get_projects_by_institution(
    db,
    institution_id,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "project_name",
    order: str = "asc"
):

    query = db.query(models.Project).filter(
        models.Project.institution_id == institution_id
    )

    # -----------------------------
    # SORTING
    # -----------------------------

    if sort_by == "project_name":
        sort_column = func.lower(models.Project.project_name)

    elif sort_by == "status":
        sort_column = func.lower(models.Project.status)

    elif sort_by == "start_date":
        sort_column = models.Project.start_date

    else:
        sort_column = func.lower(models.Project.project_name)

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # -----------------------------
    # TOTAL RECORDS
    # -----------------------------

    total_records = query.count()

    # -----------------------------
    # PAGINATION
    # -----------------------------

    pagination = get_pagination(
        page,
        page_size,
        total_records
    )

    projects = (
        query
        .offset(pagination["offset"])
        .limit(page_size)
        .all()
    )

    # -----------------------------
    # INSTITUTION NAME
    # -----------------------------

    for project in projects:

        if project.institution:
            project.institution_name = project.institution.name
        else:
            project.institution_name = None

    return projects, pagination

def get_projects_by_researcher(db, researcher_id):

    project_members = (
        db.query(models.ProjectMember)
        .filter(
            models.ProjectMember.researcher_id == researcher_id
        )
        .all()
    )

    result = []


    for member in project_members:


        project = (
            db.query(models.Project)
            .filter(
                models.Project.id == member.project_id
            )
            .first()
        )


        if project:


            # Team Members

            team_members = (
                db.query(models.ProjectMember)
                .filter(
                    models.ProjectMember.project_id == project.id
                )
                .all()
            )


            team = []

            for team_member in team_members:

                team.append({

                    "name": team_member.researcher.full_name,

                    "role": team_member.role

                })




            # Collaborating Institutions

            institution_collaborations = (
                db.query(models.InstitutionCollaboration)
                .filter(
                    models.InstitutionCollaboration.project_id == project.id
                )
                .all()
            )


            collaborating_institutions = []


            for collaboration in institution_collaborations:


                if collaboration.collaborating_institution:

                    collaborating_institutions.append(
                        collaboration.collaborating_institution.name
                    )





            result.append({


                "id": project.id,


                "project_name": project.project_name,


                "description": project.description,


                "start_date": project.start_date,


                "end_date": project.end_date,


                "status": project.status,


                "institution_name":
                    project.institution.name
                    if project.institution
                    else None,



                "team_count": len(team),


                "collaboration_count":
                    len(collaborating_institutions),



                "team": team,



                "collaborating_institutions":
                    collaborating_institutions

            })


    return result
    
def get_project(db, project_id):

    return db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()



def update_project(db, project_id, project):

    db_project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if db_project:

        if project.project_name is not None:
            db_project.project_name = project.project_name

        if project.description is not None:
            db_project.description = project.description

        if project.start_date is not None:
            db_project.start_date = project.start_date

        if project.end_date is not None:
            db_project.end_date = project.end_date

        if project.status is not None:
            db_project.status = project.status

        if project.institution_id is not None:
            db_project.institution_id = project.institution_id

        db.commit()
        db.refresh(db_project)

        # ==========================================
        # AUDIT LOG
        # ==========================================

        institution = db.query(models.Institution).filter(
            models.Institution.id == db_project.institution_id
        ).first()

        if institution:
            create_activity_log(
                db=db,
                user_id=institution.user_id,
                action="UPDATE",
                description=f"Updated project '{db_project.project_name}'"
            )

    return db_project


def delete_project(db, project_id):

    db_project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if db_project:

        # Get institution before deleting project
        institution = db.query(models.Institution).filter(
            models.Institution.id == db_project.institution_id
        ).first()

        # ==========================================
        # AUDIT LOG
        # ==========================================

        if institution:
            create_activity_log(
                db=db,
                user_id=institution.user_id,
                action="DELETE",
                description=f"Deleted project '{db_project.project_name}'"
            )

        db.delete(db_project)
        db.commit()

    return db_project
# ==========================
# Project Member CRUD
# ==========================

def create_project_member(db, member):

    # Check if researcher is already assigned
    existing_member = db.query(
        models.ProjectMember
    ).filter(
        models.ProjectMember.project_id == member.project_id,
        models.ProjectMember.researcher_id == member.researcher_id
    ).first()

    if existing_member:
        raise HTTPException(
            status_code=400,
            detail="Researcher is already assigned to this project."
        )

    # Create new assignment
    db_member = models.ProjectMember(
        project_id=member.project_id,
        researcher_id=member.researcher_id,
        role=member.role
    )

    db.add(db_member)
    db.commit()
    db.refresh(db_member)

    # =====================================
    # PROJECT AND RESEARCHER DETAILS
    # =====================================

    project = db_member.project
    researcher = db_member.researcher

    # =====================================
    # AUDIT LOG
    # =====================================

    if project and researcher:

        create_activity_log(
            db=db,
            user_id=researcher.user_id,
            action="CREATE",
            description=f"Assigned researcher '{researcher.full_name}' to project '{project.project_name}'"
        )

    # =====================================
    # PROJECT ASSIGNMENT NOTIFICATIONS
    # =====================================

    if project and researcher:

        # ---------------------------------
        # 1. Assigned Researcher Notification
        # ---------------------------------

        create_notification(
            db,
            schemas.NotificationCreate(

                receiver_id=researcher.user_id,

                sender_id=None,

                title="Project Assigned",

                message=f'You have been assigned to project "{project.project_name}".',

                notification_type="project",

                reference_id=project.id,

                reference_type="project"
            )
        )

        # ---------------------------------
        # 2. Institution Admin Notification
        # ---------------------------------

        if project.institution:

            create_notification(
                db,
                schemas.NotificationCreate(

                    receiver_id=project.institution.user_id,

                    sender_id=None,

                    title="Researcher Assigned",

                    message=f'{researcher.full_name} has been assigned to project "{project.project_name}".',

                    notification_type="project",

                    reference_id=project.id,

                    reference_type="project"
                )
            )

        # ---------------------------------
        # 3. System Admin Notification
        # ---------------------------------

        system_admins = db.query(models.User).filter(
            models.User.role == "system_admin"
        ).all()

        for admin in system_admins:

            create_notification(
                db,
                schemas.NotificationCreate(

                    receiver_id=admin.id,

                    sender_id=None,

                    title="Project Member Assigned",

                    message=f'A researcher has been assigned to project "{project.project_name}".',

                    notification_type="project",

                    reference_id=project.id,

                    reference_type="project"
                )
            )

    # =====================================
    # Automatically update project status
    # =====================================

    print("PROJECT FOUND:", project)
    print("PROJECT ID:", member.project_id)

    if project:

        print("CURRENT STATUS:", project.status)

    if project and project.status == "Planned":

        print("UPDATING STATUS TO ONGOING...")

        project.status = "Ongoing"

        db.add(project)
        db.commit()
        db.refresh(project)

        print("UPDATED STATUS:", project.status)

    return db_member
# ==========================
# Get Project Team Members
# ==========================

def get_project_members(db, project_id):

    members = (
        db.query(models.ProjectMember)
        .filter(models.ProjectMember.project_id == project_id)
        .all()
    )

    result = []

    for member in members:

        result.append({
            "id": member.id,
            "project_id": member.project_id,
            "researcher_id": member.researcher_id,
            "researcher_name": member.researcher.full_name,
            "role": member.role,
            "assigned_at": member.assigned_at
        })

    return result



# Remove Researcher from Project

def delete_project_member(db, member_id):

    member = db.query(
        models.ProjectMember
    ).filter(
        models.ProjectMember.id == member_id
    ).first()

    if member:

        # Get project and researcher details before deleting
        project = member.project
        researcher = member.researcher

        # =====================================
        # AUDIT LOG
        # =====================================

        if project and researcher:

            create_activity_log(
                db=db,
                user_id=researcher.user_id,
                action="DELETE",
                description=f"Removed researcher '{researcher.full_name}' from project '{project.project_name}'"
            )

        # Delete project member
        db.delete(member)
        db.commit()

    return member

# ==========================
# Institution Collaboration CRUD
# ==========================

def create_institution_collaboration(db, collaboration):

    existing_collaboration = db.query(
        models.InstitutionCollaboration
    ).filter(
        models.InstitutionCollaboration.project_id == collaboration.project_id,
        models.InstitutionCollaboration.collaborating_institution_id == collaboration.collaborating_institution_id
    ).first()

    if existing_collaboration:
        raise HTTPException(
            status_code=400,
            detail="This institution collaboration already exists."
        )

    db_collaboration = models.InstitutionCollaboration(
        project_id=collaboration.project_id,
        collaborating_institution_id=collaboration.collaborating_institution_id
    )

    db.add(db_collaboration)
    db.commit()
    db.refresh(db_collaboration)

    # ==========================
    # Get Project
    # ==========================

    project = db.query(models.Project).filter(
        models.Project.id == db_collaboration.project_id
    ).first()

    # ==========================
    # Automatically update project status
    # ==========================

    if project and project.status == "Planned":

        project.status = "Ongoing"

        db.commit()

    # ==========================
    # Get Institution Details
    # ==========================

    main_institution = db.query(models.Institution).filter(
        models.Institution.id == project.institution_id
    ).first()

    collaborating_institution = db.query(models.Institution).filter(
        models.Institution.id == db_collaboration.collaborating_institution_id
    ).first()

    # =====================================
    # AUDIT LOG
    # =====================================

    if project and main_institution and collaborating_institution:

        create_activity_log(
            db=db,
            user_id=main_institution.user_id,
            action="CREATE",
            description=(
                f"Created collaboration for project "
                f"'{project.project_name}' between "
                f"{main_institution.name} and "
                f"{collaborating_institution.name}"
            )
        )

    # =====================================
    # COLLABORATION NOTIFICATIONS
    # =====================================

    if project and main_institution and collaborating_institution:

        # ---------------------------------
        # Institution Admin Notification
        # ---------------------------------

        create_notification(
            db,
            schemas.NotificationCreate(

                receiver_id=main_institution.user_id,

                sender_id=None,

                title="New Collaboration Created",

                message=f'A collaboration has been created for project "{project.project_name}" with {collaborating_institution.name}.',

                notification_type="collaboration",

                reference_id=db_collaboration.id,

                reference_type="collaboration"
            )
        )

        # ---------------------------------
        # System Admin Notification
        # ---------------------------------

        system_admins = db.query(models.User).filter(
            models.User.role == "system_admin"
        ).all()

        for admin in system_admins:

            create_notification(
                db,
                schemas.NotificationCreate(

                    receiver_id=admin.id,

                    sender_id=None,

                    title="Institution Collaboration Created",

                    message=f'A new collaboration has been created between {main_institution.name} and {collaborating_institution.name}.',

                    notification_type="collaboration",

                    reference_id=db_collaboration.id,

                    reference_type="collaboration"
                )
            )

    return {

        "id": db_collaboration.id,

        "project_id": project.id,

        "project_name": project.project_name,

        "institution_id": main_institution.id,

        "institution_name": main_institution.name,

        "collaborating_institution_id": collaborating_institution.id,

        "collaborating_institution_name": collaborating_institution.name,

        "created_at": db_collaboration.created_at
    }

def get_institution_collaborations(db):

    collaborations = (
        db.query(
            models.InstitutionCollaboration.id,
            models.InstitutionCollaboration.project_id,
            models.InstitutionCollaboration.collaborating_institution_id,
            models.Project.project_name,
            models.Project.institution_id,
            models.Institution.name.label("institution_name"),
            models.InstitutionCollaboration.created_at
        )
        .join(
            models.Project,
            models.InstitutionCollaboration.project_id == models.Project.id
        )
        .join(
            models.Institution,
            models.Project.institution_id == models.Institution.id
        )
        .all()
    )


    result = []


    for item in collaborations:


        collaborating_institution = (
            db.query(models.Institution.name)
            .filter(
                models.Institution.id ==
                item.collaborating_institution_id
            )
            .first()
        )


        result.append({

            "id": item.id,

            "project_id": item.project_id,

            "project_name": item.project_name,

            "institution_id": item.institution_id,

            "institution_name": item.institution_name,

            "collaborating_institution_id": item.collaborating_institution_id,

            "collaborating_institution_name":
                collaborating_institution[0]
                if collaborating_institution
                else None,

            "created_at": item.created_at
        })


    return result
def delete_institution_collaboration(db, collaboration_id):

    collaboration = db.query(
        models.InstitutionCollaboration
    ).filter(
        models.InstitutionCollaboration.id == collaboration_id
    ).first()

    if collaboration:

        # Get project details before deleting
        project = db.query(models.Project).filter(
            models.Project.id == collaboration.project_id
        ).first()

        # Get main institution
        main_institution = None

        if project:
            main_institution = db.query(
                models.Institution
            ).filter(
                models.Institution.id == project.institution_id
            ).first()

        # Get collaborating institution
        collaborating_institution = db.query(
            models.Institution
        ).filter(
            models.Institution.id == collaboration.collaborating_institution_id
        ).first()

        # =====================================
        # AUDIT LOG
        # =====================================

        if (
            project
            and main_institution
            and collaborating_institution
        ):

            create_activity_log(
                db=db,
                user_id=main_institution.user_id,
                action="DELETE",
                description=(
                    f"Deleted collaboration for project "
                    f"'{project.project_name}' between "
                    f"{main_institution.name} and "
                    f"{collaborating_institution.name}"
                )
            )

        # Delete collaboration
        db.delete(collaboration)
        db.commit()

    return collaboration
def create_activity(
    db,
    user_id: int,
    action: str,
    description: str
):

    print(
        "CREATING ACTIVITY:",
        user_id,
        action,
        description
    )

    activity = models.ActivityLog(
        user_id=user_id,
        action=action,
        description=description
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    print(
        "ACTIVITY CREATED:",
        activity.id
    )

    return activity

from datetime import datetime, timedelta

def get_recent_activities(
    db,
    current_user,
    limit: int = 5
):
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    # =========================================
    # SYSTEM ADMIN
    # See important system-wide activities
    # =========================================

    if current_user.role == "system_admin":

        return (
            db.query(models.ActivityLog)
            .filter(
                models.ActivityLog.created_at >= seven_days_ago
            )
            .order_by(
                models.ActivityLog.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    # =========================================
    # RESEARCHER
    # Own activities
    # =========================================

    elif current_user.role == "researcher":

        return (
            db.query(models.ActivityLog)
            .filter(
                models.ActivityLog.user_id == current_user.id,
                models.ActivityLog.created_at >= seven_days_ago
            )
            .order_by(
                models.ActivityLog.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    # =========================================
    # REVIEWER
    # Own activities
    # =========================================

    elif current_user.role == "reviewer":

        return (
            db.query(models.ActivityLog)
            .filter(
                models.ActivityLog.user_id == current_user.id,
                models.ActivityLog.created_at >= seven_days_ago
            )
            .order_by(
                models.ActivityLog.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    # =========================================
    # INSTITUTION ADMIN
    # Recent activities
    #
    # Flask will receive the recent activities
    # and display the latest 5.
    # =========================================

    elif current_user.role == "institution_admin":

        return (
            db.query(models.ActivityLog)
            .filter(
                models.ActivityLog.created_at >= seven_days_ago
            )
            .order_by(
                models.ActivityLog.created_at.desc()
            )
            .limit(100)
            .all()
        )

    # =========================================
    # DEFAULT
    # =========================================

    return []
# ==========================
# CITATION CRUD
# ==========================


def create_citation(
    db: Session,
    citation: schemas.CitationCreate,
    creator_user_id: int,
    creator_role: str
):

    # Check citing publication exists
    publication = db.query(models.Publication).filter(
        models.Publication.id == citation.publication_id
    ).first()

    if not publication:
        raise ValueError(
            "Publication not found"
        )

    # Check cited publication exists
    cited_publication = db.query(models.Publication).filter(
        models.Publication.id == citation.cited_publication_id
    ).first()

    if not cited_publication:
        raise ValueError(
            "Cited publication not found"
        )

    # Cannot cite itself
    if citation.publication_id == citation.cited_publication_id:
        raise ValueError(
            "A publication cannot cite itself"
        )

    # Only published papers can be cited
    if cited_publication.status != "Published":
        raise ValueError(
            "Only published publications can be cited"
        )

    # Prevent duplicate citation
    existing_citation = db.query(models.Citation).filter(
        models.Citation.publication_id == citation.publication_id,
        models.Citation.cited_publication_id == citation.cited_publication_id
    ).first()

    if existing_citation:
        raise ValueError(
            "Citation already exists"
        )

    # Create citation
    db_citation = models.Citation(
        publication_id=citation.publication_id,
        cited_publication_id=citation.cited_publication_id
    )

    db.add(db_citation)

    db.commit()

    db.refresh(db_citation)

    # =====================================
    # AUDIT LOG
    # =====================================

    create_activity_log(
        db=db,
        user_id=creator_user_id,
        action="CREATE",
        description=(
            f'Added citation from publication '
            f'"{publication.title}" to '
            f'"{cited_publication.title}"'
        )
    )

    # =====================================
    # CITATION NOTIFICATIONS
    # =====================================

    # Get Publication Owner

    publication_owner = db.query(models.Researcher).filter(
        models.Researcher.id == publication.researcher_id
    ).first()

    if publication_owner:

        # =================================
        # Researcher Notification
        # =================================

        if publication_owner.user_id != creator_user_id:

            create_notification(
                db,
                schemas.NotificationCreate(

                    receiver_id=publication_owner.user_id,

                    sender_id=creator_user_id,

                    title="Citation Added",

                    message=f'A citation has been added to your publication "{publication.title}".',

                    notification_type="citation",

                    reference_id=db_citation.id,

                    reference_type="citation"
                )
            )

        # =================================
        # Institution Admin Notification
        # =================================

        institution = db.query(models.Institution).filter(
            models.Institution.name == publication_owner.institution
        ).first()

        if institution and institution.user_id != creator_user_id:

            create_notification(
                db,
                schemas.NotificationCreate(

                    receiver_id=institution.user_id,

                    sender_id=creator_user_id,

                    title="Citation Added",

                    message=f'A citation has been added to publication "{publication.title}".',

                    notification_type="citation",

                    reference_id=db_citation.id,

                    reference_type="citation"
                )
            )

    # =================================
    # System Admin Notification
    # =================================

    system_admins = db.query(models.User).filter(
        models.User.role == "system_admin"
    ).all()

    print("SYSTEM ADMINS FOUND:", system_admins)

    for admin in system_admins:

        create_notification(
            db,
            schemas.NotificationCreate(

                receiver_id=admin.id,

                sender_id=creator_user_id,

                title="Citation Added",

                message=f'A new citation has been added to publication "{publication.title}".',

                notification_type="citation",

                reference_id=db_citation.id,

                reference_type="citation"
            )
        )

    return db_citation


def get_all_citations(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "date",
    order: str = "desc"
):

    query = db.query(models.Citation)

    # Sorting by date
    if order == "asc":
        query = query.order_by(
            models.Citation.created_at.asc()
        )
    else:
        query = query.order_by(
            models.Citation.created_at.desc()
        )

    # Total records
    total_records = query.count()

    # Pagination
    pagination = get_pagination(
        page,
        page_size,
        total_records
    )

    citations = (
        query
        .offset(pagination["offset"])
        .limit(page_size)
        .all()
    )

    return citations, pagination

def get_citations_by_publication(
    db: Session,
    publication_id: int
):

    return db.query(models.Citation).filter(
        models.Citation.publication_id == publication_id
    ).all()



def get_citation_by_id(
    db: Session,
    citation_id: int
):

    return db.query(models.Citation).filter(
        models.Citation.id == citation_id
    ).first()



def delete_citation(
    db: Session,
    citation_id: int
):

    db_citation = db.query(models.Citation).filter(
        models.Citation.id == citation_id
    ).first()

    if db_citation:

        # Get publication details before deleting
        publication = db.query(models.Publication).filter(
            models.Publication.id == db_citation.publication_id
        ).first()

        cited_publication = db.query(models.Publication).filter(
            models.Publication.id == db_citation.cited_publication_id
        ).first()

        # =====================================
        # AUDIT LOG
        # =====================================

        if publication and cited_publication:

            # Get the owner of the citing publication
            researcher = db.query(models.Researcher).filter(
                models.Researcher.id == publication.researcher_id
            ).first()

            if researcher:

                create_activity_log(
                    db=db,
                    user_id=researcher.user_id,
                    action="DELETE",
                    description=(
                        f'Deleted citation from publication '
                        f'"{publication.title}" to '
                        f'"{cited_publication.title}"'
                    )
                )

        # Delete citation
        db.delete(db_citation)
        db.commit()

    return db_citation

# ==========================
# Reference CRUD
# ==========================


def create_reference(
    db: Session,
    reference: schemas.ReferenceCreate,
    creator_user_id: int,
    creator_role: str
):

    # Check publication exists
    publication = db.query(models.Publication).filter(
        models.Publication.id == reference.publication_id
    ).first()

    if not publication:
        raise ValueError(
            "Publication not found"
        )

    # Prevent duplicate reference
    existing_reference = db.query(models.Reference).filter(
        models.Reference.publication_id == reference.publication_id,
        models.Reference.reference_title == reference.reference_title
    ).first()

    if existing_reference:
        raise ValueError(
            "Reference already exists for this publication"
        )

    # Create reference
    db_reference = models.Reference(
        publication_id=reference.publication_id,
        reference_title=reference.reference_title,
        author=reference.author,
        publication_year=reference.publication_year,
        doi=reference.doi
    )

    db.add(db_reference)
    db.commit()
    db.refresh(db_reference)

    # =====================================
    # AUDIT LOG
    # =====================================

    create_activity_log(
        db=db,
        user_id=creator_user_id,
        action="CREATE",
        description=f'Created reference "{db_reference.reference_title}" for publication "{publication.title}"'
    )

    # =====================================
    # REFERENCE NOTIFICATIONS
    # =====================================

    # Get Publication Owner
    publication_owner = db.query(models.Researcher).filter(
        models.Researcher.id == publication.researcher_id
    ).first()

    if publication_owner:

        # =================================
        # Researcher Notification
        # =================================

        if publication_owner.user_id != creator_user_id:

            create_notification(
                db,
                schemas.NotificationCreate(

                    receiver_id=publication_owner.user_id,

                    sender_id=creator_user_id,

                    title="Reference Added",

                    message=f'A new reference has been added to your publication "{publication.title}".',

                    notification_type="reference",

                    reference_id=db_reference.id,

                    reference_type="reference"

                )
            )

        # =================================
        # Institution Admin Notification
        # =================================

        institution = db.query(models.Institution).filter(
            models.Institution.name == publication_owner.institution
        ).first()

        if institution and institution.user_id != creator_user_id:

            create_notification(
                db,
                schemas.NotificationCreate(

                    receiver_id=institution.user_id,

                    sender_id=creator_user_id,

                    title="Reference Added",

                    message=f'A new reference has been added to publication "{publication.title}".',

                    notification_type="reference",

                    reference_id=db_reference.id,

                    reference_type="reference"

                )
            )

    # =================================
    # System Admin Notification
    # =================================

    system_admins = db.query(models.User).filter(
        models.User.role == "system_admin"
    ).all()

    for admin in system_admins:

        if admin.id != creator_user_id:

            create_notification(
                db,
                schemas.NotificationCreate(

                    receiver_id=admin.id,

                    sender_id=creator_user_id,

                    title="Reference Added",

                    message=f'A new reference has been added to publication "{publication.title}".',

                    notification_type="reference",

                    reference_id=db_reference.id,

                    reference_type="reference"

                )
            )

    return db_reference

def get_all_references(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "year",
    order: str = "desc"
):
    query = db.query(models.Reference)

    # -----------------------------
    # SORTING
    # -----------------------------

    if sort_by == "title":
        sort_column = models.Reference.reference_title
    else:
        sort_column = models.Reference.publication_year

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # -----------------------------
    # TOTAL RECORDS
    # -----------------------------

    total_records = query.count()

    # -----------------------------
    # PAGINATION
    # -----------------------------

    pagination = get_pagination(
        page,
        page_size,
        total_records
    )

    references = (
        query
        .offset(pagination["offset"])
        .limit(page_size)
        .all()
    )

    return references, pagination
    
def get_references_by_publication(
    db: Session,
    publication_id: int
):

    return db.query(models.Reference).filter(
        models.Reference.publication_id == publication_id
    ).all()



def get_reference_by_id(
    db: Session,
    reference_id: int
):

    return db.query(models.Reference).filter(
        models.Reference.id == reference_id
    ).first()



def delete_reference(
    db: Session,
    reference_id: int
):

    db_reference = db.query(models.Reference).filter(
        models.Reference.id == reference_id
    ).first()

    if db_reference:

        # Save details before deleting
        reference_title = db_reference.reference_title
        publication_id = db_reference.publication_id

        # DELETE AUDIT LOG
        create_activity_log(
            db=db,
            user_id=None,
            action="DELETE",
            description=f'Deleted reference "{reference_title}" from publication ID {publication_id}'
        )

        db.delete(db_reference)
        db.commit()

    return db_reference
    
def create_notification(
        db,
        notification
):

    new_notification = Notification(
        receiver_id=notification.receiver_id,
        sender_id=notification.sender_id,
        title=notification.title,
        message=notification.message,
        notification_type=notification.notification_type,
        reference_id=notification.reference_id,
        reference_type=notification.reference_type
    )


    db.add(new_notification)

    db.commit()

    db.refresh(new_notification)

    return new_notification
def get_user_notifications(
        db,
        user_id
):

    return db.query(Notification)\
        .filter(
            Notification.receiver_id == user_id
        )\
        .order_by(
            Notification.created_at.desc()
        )\
        .all()
def mark_notification_read(
        db,
        notification_id
):

    notification = db.query(Notification)\
        .filter(
            Notification.id == notification_id
        )\
        .first()


    if notification:

        notification.is_read = True

        db.commit()

        db.refresh(notification)


    return notification

# ==========================
# REVIEW CRUD
# ==========================

def get_pending_reviews(db: Session):

    return db.query(models.Publication).filter(
        models.Publication.status == "Under Review"
    ).all()


def create_review(
    db: Session,
    review: schemas.ReviewCreate,
    reviewer_id: int
):

    # Only reviewer can create review
    reviewer = db.query(models.User).filter(
        models.User.id == reviewer_id,
        models.User.role == "reviewer"
    ).first()

    if not reviewer:
        raise HTTPException(
            status_code=403,
            detail="Only reviewers can review publications"
        )

    # Get publication
    publication = db.query(models.Publication).filter(
        models.Publication.id == review.publication_id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    # Publication must be under review
    if publication.status != "Under Review":
        raise HTTPException(
            status_code=400,
            detail="Publication is not pending review"
        )

    # Prevent multiple reviews
    existing_review = db.query(models.Review).filter(
        models.Review.publication_id == review.publication_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="Publication has already been reviewed"
        )

    # Validate decision
    if review.decision not in ["Published", "Rejected"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid review decision"
        )

    # Create review
    db_review = models.Review(
        publication_id=review.publication_id,
        reviewer_id=reviewer_id,
        decision=review.decision,
        comments=review.comments
    )

    db.add(db_review)

    # Update publication status
    publication.status = review.decision

    db.commit()
    db.refresh(db_review)

    # =====================================
    # AUDIT LOG
    # =====================================

    create_activity_log(
        db=db,
        user_id=reviewer_id,
        action="CREATE",
        description=f'Reviewed publication "{publication.title}" - Decision: {review.decision}'
    )

    # =====================================
    # REVIEW NOTIFICATIONS
    # =====================================

    # Get Publication Owner
    publication_owner = db.query(models.Researcher).filter(
        models.Researcher.id == publication.researcher_id
    ).first()

    if publication_owner:

        # ---------------------------------
        # 1. Researcher Notification
        # ---------------------------------

        create_notification(
            db,
            schemas.NotificationCreate(
                receiver_id=publication_owner.user_id,
                sender_id=reviewer_id,
                title="Publication Review Completed",
                message=f'Your publication "{publication.title}" has been {review.decision.lower()}.',
                notification_type="review",
                reference_id=db_review.id,
                reference_type="review"
            )
        )

        # ---------------------------------
        # 2. Institution Admin Notification
        # ---------------------------------

        institution = db.query(models.Institution).filter(
            models.Institution.name == publication_owner.institution
        ).first()

        if institution:

            create_notification(
                db,
                schemas.NotificationCreate(
                    receiver_id=institution.user_id,
                    sender_id=reviewer_id,
                    title="Publication Review Completed",
                    message=f'The publication "{publication.title}" by {publication_owner.full_name} has been {review.decision.lower()}.',
                    notification_type="review",
                    reference_id=db_review.id,
                    reference_type="review"
                )
            )

    # ---------------------------------
    # 3. System Admin Notification
    # ---------------------------------

    system_admins = db.query(models.User).filter(
        models.User.role == "system_admin"
    ).all()

    for admin in system_admins:

        create_notification(
            db,
            schemas.NotificationCreate(
                receiver_id=admin.id,
                sender_id=reviewer_id,
                title="Publication Review Completed",
                message=f'The publication "{publication.title}" has been {review.decision.lower()} by a reviewer.',
                notification_type="review",
                reference_id=db_review.id,
                reference_type="review"
            )
        )

    return db_review