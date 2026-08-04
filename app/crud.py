from sqlalchemy.orm import Session
from app import models, schemas, auth


# ---------------- USERS ----------------

def create_user(db: Session, user: schemas.UserCreate):

    hashed_password = auth.hash_password(user.password)

    db_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(
        models.User.email == email
    ).first()



# ---------------- RESEARCHERS ----------------

def create_researcher(
    db: Session,
    researcher: schemas.ResearcherCreate
):

    db_researcher = models.Researcher(
        full_name=researcher.full_name,
        department=researcher.department,
        skills=researcher.skills,
        research_interest=researcher.research_interest,
        designation=researcher.designation,
        institution_id=researcher.institution_id
    )

    db.add(db_researcher)
    db.commit()
    db.refresh(db_researcher)

    return db_researcher



def get_researchers(db: Session):
    return db.query(models.Researcher).all()


def count_projects(db: Session):
    return db.query(models.Project).count()



def get_researcher_by_id(db: Session, id: int):
    return db.query(models.Researcher).filter(
        models.Researcher.id == id
    ).first()



def update_researcher(
    db: Session,
    id: int,
    updated: schemas.ResearcherCreate
):

    researcher = get_researcher_by_id(db, id)

    if not researcher:
        return None


    researcher.full_name = updated.full_name
    researcher.department = updated.department
    researcher.skills = updated.skills
    researcher.research_interest = updated.research_interest
    researcher.designation = updated.designation
    researcher.institution_id = updated.institution_id


    db.commit()
    db.refresh(researcher)

    return researcher



# ---------------- INSTITUTIONS ----------------

def create_institution(
    db: Session,
    institution: schemas.InstitutionCreate
):

    db_institution = models.Institution(
        name=institution.name,
        address=institution.address,
        website=institution.website,
        contact_email=institution.contact_email
    )

    db.add(db_institution)
    db.commit()
    db.refresh(db_institution)

    return db_institution



def get_institutions(db: Session):
    return db.query(models.Institution).all()



def get_institution_by_id(
    db: Session,
    institution_id: int
):

    return db.query(models.Institution).filter(
        models.Institution.id == institution_id
    ).first()



def update_institution(
    db: Session,
    institution_id: int,
    updated_institution: schemas.InstitutionCreate
):

    institution = get_institution_by_id(
        db,
        institution_id
    )

    if not institution:
        return None


    institution.name = updated_institution.name
    institution.address = updated_institution.address
    institution.website = updated_institution.website
    institution.contact_email = updated_institution.contact_email


    db.commit()
    db.refresh(institution)

    return institution



def delete_institution(
    db: Session,
    institution_id: int
):

    institution = get_institution_by_id(
        db,
        institution_id
    )

    if not institution:
        return None


    db.delete(institution)
    db.commit()

    return institution




# ---------------- PUBLICATIONS ----------------


def create_publication(
    db: Session,
    publication: schemas.PublicationCreate
):

    # Get researchers
    researchers = db.query(models.Researcher).filter(
        models.Researcher.id.in_(publication.researcher_ids)
    ).all()


    # Create publication

    db_publication = models.Publication(

        title=publication.title,

        abstract=publication.abstract,

        publication_type=publication.publication_type,

        status=publication.status,

        doi=publication.doi,

        publication_date=publication.publication_date,

        journal_or_venue=publication.journal_or_venue,

        institution_id=publication.institution_id
    )


    # Attach authors

    db_publication.authors = researchers


    db.add(db_publication)

    db.commit()

    db.refresh(db_publication)



    # -----------------------------------
    # CREATE COLLABORATION NETWORK
    # -----------------------------------

    if len(researchers) > 1:


        for i in range(len(researchers)):

            for j in range(i + 1, len(researchers)):


                collaboration = models.Collaboration(

                    researcher1_id=researchers[i].id,

                    researcher2_id=researchers[j].id,

                    publication_id=db_publication.id

                )


                db.add(collaboration)



        db.commit()



    return db_publication




def get_publications(db: Session):

    return db.query(models.Publication).all()



def get_publication_by_id(
    db: Session,
    publication_id: int
):

    return db.query(models.Publication).filter(
        models.Publication.id == publication_id
    ).first()



def get_publications_by_status(
    db: Session,
    status: str
):

    return db.query(models.Publication).filter(
        models.Publication.status == status
    ).all()



def get_publications_by_institution(
    db: Session,
    institution_id: int
):

    return db.query(models.Publication).filter(
        models.Publication.institution_id == institution_id
    ).all()



def update_publication(
    db: Session,
    publication_id: int,
    updated_publication: schemas.PublicationCreate
):

    publication = get_publication_by_id(
        db,
        publication_id
    )


    if not publication:
        return None



    publication.title = updated_publication.title
    publication.abstract = updated_publication.abstract
    publication.publication_type = updated_publication.publication_type
    publication.status = updated_publication.status
    publication.doi = updated_publication.doi
    publication.publication_date = updated_publication.publication_date
    publication.journal_or_venue = updated_publication.journal_or_venue
    publication.institution_id = updated_publication.institution_id



    db.commit()
    db.refresh(publication)

    return publication




def delete_publication(
    db: Session,
    publication_id: int
):

    publication = get_publication_by_id(
        db,
        publication_id
    )


    if not publication:
        return None


    db.delete(publication)

    db.commit()

    return publication





# ---------------- CONFERENCES ----------------


def create_conference(
    db: Session,
    conference: schemas.ConferenceCreate
):

    db_conf = models.Conference(
        **conference.dict()
    )


    db.add(db_conf)

    db.commit()

    db.refresh(db_conf)

    return db_conf



def get_conferences(db: Session):

    return db.query(models.Conference).all()



def get_conference_by_id(
    db: Session,
    conference_id: int
):

    return db.query(models.Conference).filter(
        models.Conference.id == conference_id
    ).first()



def register_participation(
    db: Session,
    participation: schemas.ConferenceParticipationCreate
):

    db_part = models.ConferenceParticipation(
        **participation.dict()
    )


    db.add(db_part)

    db.commit()

    db.refresh(db_part)

    return db_part



def get_participants_by_conference(
    db: Session,
    conference_id: int
):

    return db.query(
        models.ConferenceParticipation
    ).filter(
        models.ConferenceParticipation.conference_id == conference_id
    ).all()



def get_conferences_by_researcher(
    db: Session,
    researcher_id: int
):

    return db.query(
        models.ConferenceParticipation
    ).filter(
        models.ConferenceParticipation.researcher_id == researcher_id
    ).all()


# ---------------- COLLABORATIONS ----------------

def create_collaboration(
    db: Session,
    collaboration: schemas.CollaborationCreate
):

    db_collaboration = models.Collaboration(
        researcher1_id=collaboration.researcher1_id,
        researcher2_id=collaboration.researcher2_id,
        project=collaboration.project,
        publication_id=collaboration.publication_id
    )

    db.add(db_collaboration)
    db.commit()
    db.refresh(db_collaboration)

    return db_collaboration


def get_collaborations(db: Session):
    return db.query(models.Collaboration).all()


def get_collaboration_by_id(db: Session, collaboration_id: int):
    return db.query(models.Collaboration).filter(
        models.Collaboration.id == collaboration_id
    ).first()


def update_collaboration(
    db: Session,
    collaboration_id: int,
    collaboration: schemas.CollaborationCreate
):
    record = get_collaboration_by_id(db, collaboration_id)
    if not record:
        return None
    record.researcher1_id = collaboration.researcher1_id
    record.researcher2_id = collaboration.researcher2_id
    record.project = collaboration.project
    record.publication_id = collaboration.publication_id
    db.commit()
    db.refresh(record)
    return record


def delete_collaboration(db: Session, collaboration_id: int):
    record = get_collaboration_by_id(db, collaboration_id)
    if not record:
        return None
    db.delete(record)
    db.commit()
    return record


def create_citation(
    db: Session,
    citation: schemas.CitationCreate
):
    db_citation = models.Citation(
        citing_publication_id=citation.citing_publication_id,
        cited_publication_id=citation.cited_publication_id
    )
    db.add(db_citation)
    db.commit()
    db.refresh(db_citation)
    return db_citation


def get_citations(db: Session):
    return db.query(models.Citation).all()


# ---------------- PROJECTS ----------------
def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_projects(db: Session):
    return db.query(models.Project).all()


def get_project_by_id(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def add_project_assignment(db: Session, project_id: int, assignment: schemas.ProjectAssignmentCreate):
    db_assignment = models.ProjectAssignment(project_id=project_id, **assignment.model_dump())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def count_researchers(db: Session):
    return db.query(models.Researcher).count()


def count_publications(db: Session):
    return db.query(models.Publication).count()


def count_collaborations(db: Session):
    return db.query(models.Collaboration).count()


def count_institutions(db: Session):
    return db.query(models.Institution).count()


def count_citations(db: Session):
    return db.query(models.Citation).count()




# ---------------- REPORTS ----------------


def get_institution_report(
    db: Session,
    institution_id: int
):

    researchers = db.query(
        models.Researcher
    ).filter(
        models.Researcher.institution_id == institution_id
    ).count()


    publications = db.query(
        models.Publication
    ).filter(
        models.Publication.institution_id == institution_id
    ).count()



    return {
        "institution_id": institution_id,
        "researchers": researchers,
        "publications": publications
    }
