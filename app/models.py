from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, date
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(100), nullable=False)

    email = Column(String(100), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    role = Column(String(50), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

class Researcher(Base):
    __tablename__ = "researchers"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True
    )

    full_name = Column(String(100), nullable=False)

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    department = Column(String(100), nullable=False)

    institution = Column(String(150), nullable=False)

    designation = Column(String(100), nullable=False)

    research_interests = Column(String(255), nullable=True)

    skills = Column(String(255), nullable=True)

    phone = Column(String(20), nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    publications = relationship(
        "Publication",
        back_populates="researcher"
    )
class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)

    researcher_id = Column(
        Integer,
        ForeignKey("researchers.id")
    )

    title = Column(String(255), nullable=False)

    publication_type = Column(String(100), nullable=False)

    journal_name = Column(String(255))

    conference_name = Column(String(255))

    publication_year = Column(Integer)

    doi = Column(String(100))

    status = Column(String(50))

    publication_file = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)

    researcher = relationship(
        "Researcher",
         back_populates="publications"
    )

class Citation(Base):

    __tablename__ = "citations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    # Publication creating the citation
    publication_id = Column(
        Integer,
        ForeignKey(
            "publications.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )


    # Publication being cited
    cited_publication_id = Column(
        Integer,
        ForeignKey(
            "publications.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    publication = relationship(
        "Publication",
        foreign_keys=[publication_id]
    )


    cited_publication = relationship(
        "Publication",
        foreign_keys=[cited_publication_id]
    )
    
class Reference(Base):

    __tablename__ = "references"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    # Publication which contains this reference
    publication_id = Column(
        Integer,
        ForeignKey("publications.id"),
        nullable=False
    )


    reference_title = Column(
        String(255),
        nullable=False
    )


    author = Column(
        String(255)
    )


    publication_year = Column(
        Integer
    )


    doi = Column(
        String(100)
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    publication = relationship(
        "Publication"
    )
    
class Institution(Base):

    __tablename__ = "institutions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True
    )

    name = Column(
        String(150),
        unique=True,
        nullable=False
    )

    institution_type = Column(
        String(100)
    )

    location = Column(
        String(150),
        nullable=False
    )

    website = Column(
        String(255)
    )

    phone = Column(
        String(20)
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
class Conference(Base):

    __tablename__ = "conferences"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    title = Column(
        String(255),
        nullable=False
    )


    organizer = Column(
        String(255),
        nullable=False
    )


    location = Column(
        String(150),
        nullable=False
    )


    conference_date = Column(
        String(50),
        nullable=False
    )


    website = Column(
        String(255)
    )


    institution = Column(
        String(150)
    )


    event_type = Column(
        String(100)
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

class ConferenceRegistration(Base):

    __tablename__ = "conference_registrations"

    id = Column(Integer, primary_key=True, index=True)

    researcher_id = Column(
        Integer,
        ForeignKey("researchers.id"),
        nullable=False
    )

    conference_id = Column(
        Integer,
        ForeignKey("conferences.id"),
        nullable=False
    )

    participation_type = Column(
        String(50),
        nullable=False
    )

    presentation_title = Column(
        String(255),
        nullable=True
    )

    publication_id = Column(
        Integer,
        nullable=True
    )

    presentation_mode = Column(
        String(50),
        nullable=True
    )

    status = Column(
        String(50),
        default="Registered"
    )

    registration_date = Column(
        Date,
        default=date.today
    )


    researcher = relationship(
        "Researcher"
    )


    conference = relationship(
        "Conference"
    )
class Project(Base):

    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    project_name = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    start_date = Column(
        Date,
        nullable=False
    )

    end_date = Column(
        Date,
        nullable=True
    )

    status = Column(
        String(50),
        default="Planned"
    )

    institution_id = Column(
        Integer,
        ForeignKey("institutions.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    institution = relationship(
        "Institution"
    )
class ProjectMember(Base):

    __tablename__ = "project_members"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )


    researcher_id = Column(
        Integer,
        ForeignKey("researchers.id"),
        nullable=False
    )


    role = Column(
        String(100),
        default="Team Member"
    )


    assigned_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    project = relationship(
        "Project"
    )


    researcher = relationship(
        "Researcher"
    )
class InstitutionCollaboration(Base):

    __tablename__ = "institution_collaborations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    collaborating_institution_id = Column(
        Integer,
        ForeignKey("institutions.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    project = relationship("Project")

    collaborating_institution = relationship("Institution")

class ActivityLog(Base):

    __tablename__ = "activity_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    action = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship("User")

class Notification(Base):

    __tablename__ = "notifications"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    # User receiving notification
    receiver_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )


    # User who triggered the action
    sender_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )


    title = Column(
        String(255),
        nullable=False
    )


    message = Column(
        Text,
        nullable=False
    )


    notification_type = Column(
        String(50),
        nullable=False
    )
  
    # Used for redirecting user when clicked
    reference_id = Column(
        Integer,
        nullable=True
    )


    reference_type = Column(
        String(50),
        nullable=True
    )
    


    is_read = Column(
        Boolean,
        default=False
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    receiver = relationship(
        "User",
        foreign_keys=[receiver_id]
    )


    sender = relationship(
        "User",
        foreign_keys=[sender_id]
    )

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    publication_id = Column(
        Integer,
        ForeignKey("publications.id", ondelete="CASCADE"),
        nullable=False
    )

    reviewer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    decision = Column(
        String(50),
        nullable=False
    )

    comments = Column(
        Text,
        nullable=True
    )

    reviewed_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    publication = relationship("Publication")

    reviewer = relationship(
        "User",
        foreign_keys=[reviewer_id]
    )