from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException

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

    return db_researcher


def get_all_researchers(db: Session):
    return db.query(models.Researcher).all()


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
    update_data = researcher.model_dump(exclude_unset=True)


    # Update researcher table
    for key, value in update_data.items():
        setattr(db_researcher, key, value)


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

    return db_researcher

def delete_researcher(db: Session, researcher_id: int):
    db_researcher = db.query(models.Researcher).filter(
        models.Researcher.id == researcher_id
    ).first()

    if db_researcher:
        db.delete(db_researcher)
        db.commit()

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

    return db_publication

def get_all_publications(db: Session):
    return db.query(models.Publication).all()


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
        and update_data.get("status", db_publication.status) != "Published"
    ):
        raise HTTPException(
            status_code=400,
            detail="DOI can be added only for published publications"
        )


    for key, value in update_data.items():
        setattr(
            db_publication,
            key,
            value
        )


    db.commit()
    db.refresh(db_publication)


    return db_publication
def delete_publication(db: Session, publication_id: int):
    db_publication = db.query(models.Publication).filter(
        models.Publication.id == publication_id
    ).first()

    if db_publication:
        db.delete(db_publication)
        db.commit()

    return db_publication
def create_institution(db: Session, institution: schemas.InstitutionCreate):
    db_institution = models.Institution(**institution.model_dump())

    db.add(db_institution)
    db.commit()
    db.refresh(db_institution)

    return db_institution


def get_all_institutions(db: Session):
    return db.query(models.Institution).all()


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

    return db_institution


def delete_institution(db: Session, institution_id: int):
    db_institution = db.query(models.Institution).filter(
        models.Institution.id == institution_id
    ).first()

    if db_institution:
        db.delete(db_institution)
        db.commit()

    return db_institution
def get_conferences_by_institution(
    db: Session,
    institution_name: str
):
    return db.query(models.Conference).filter(
        models.Conference.institution == institution_name
    ).all()
    
def create_conference(db: Session, conference: schemas.ConferenceCreate):
    db_conference = models.Conference(**conference.model_dump())
    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)
    return db_conference


def get_all_conferences(db: Session):
    return db.query(models.Conference).all()


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


    return db_conference

def delete_conference(db: Session, conference_id: int):
    db_conference = db.query(models.Conference).filter(
        models.Conference.id == conference_id
    ).first()

    if db_conference:
        db.delete(db_conference)
        db.commit()

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

        db.delete(registration)

        db.commit()


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

    return db_project



def get_projects(db):

    projects = db.query(models.Project).all()

    for project in projects:

        if project.institution:
            project.institution_name = project.institution.name
        else:
            project.institution_name = None

    return projects

def get_projects_by_institution(db, institution_id):

    projects = db.query(models.Project).filter(
        models.Project.institution_id == institution_id
    ).all()


    for project in projects:

        if project.institution:
            project.institution_name = project.institution.name

        else:
            project.institution_name = None


    return projects

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


    return db_project



def delete_project(db, project_id):

    db_project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()


    if db_project:

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

    # ==========================
    # Automatically update project status
    # ==========================

    project = db.query(models.Project).filter(
        models.Project.id == member.project_id
    ).first()

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

    collaboration = db.query(models.InstitutionCollaboration).filter(
        models.InstitutionCollaboration.id == collaboration_id
    ).first()

    if collaboration:
        db.delete(collaboration)
        db.commit()

    return collaboration
def create_activity(
    db,
    user_id: int,
    action: str,
    description: str
):

    activity = models.ActivityLog(

        user_id=user_id,

        action=action,

        description=description

    )

    db.add(activity)

    db.commit()

    db.refresh(activity)

    return activity
def get_recent_activities(
    db,
    limit: int = 5
):

    return (

        db.query(models.ActivityLog)

        .order_by(models.ActivityLog.created_at.desc())

        .limit(limit)

        .all()

    )

# ==========================
# CITATION CRUD
# ==========================


def create_citation(
    db: Session,
    citation: schemas.CitationCreate
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


    return db_citation



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

        db.delete(db_citation)
        db.commit()


    return db_citation

# ==========================
# Reference CRUD
# ==========================


def create_reference(
    db: Session,
    reference: schemas.ReferenceCreate
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


    return db_reference



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

        db.delete(db_reference)
        db.commit()


    return db_reference