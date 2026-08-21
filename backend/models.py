from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


# =====================================================
# Researcher Model
# =====================================================

class Researcher(Base):
    __tablename__ = "researchers"

    researcher_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    institution = Column(String(150))
    department = Column(String(100))
    country = Column(String(100))


# =====================================================
# User Model
# =====================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


# =====================================================
# File Model
# =====================================================

class File(Base):
    __tablename__ = "files"

    file_id = Column(Integer, primary_key=True, index=True)
    researcher_id = Column(Integer)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255))
    uploaded_set = Column(String(100))


# =====================================================
# Publication Model
# =====================================================

class Publication(Base):
    __tablename__ = "publications"

    publication_id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)
    abstract = Column(String(1000))
    keywords = Column(String(300))
    author = Column(String(150), nullable=False)
    journal = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(String(50), default="Draft")
    pdf_file = Column(String(255))

    researcher_id = Column(
        Integer,
        ForeignKey("researchers.researcher_id"),
        nullable=False
    )
    # =====================================================
# Collaboration Model
# =====================================================

class Collaboration(Base):
    __tablename__ = "collaborations"

    collaboration_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    researcher1_id = Column(
        Integer,
        ForeignKey("researchers.researcher_id"),
        nullable=False
    )

    researcher2_id = Column(
        Integer,
        ForeignKey("researchers.researcher_id"),
        nullable=False
    )

    project = Column(
        String(200),
        nullable=False
    )

    institution = Column(
        String(200)
    )

    collaboration_type = Column(
        String(100)
    )

    start_date = Column(
        String(100)
    )

    status = Column(
        String(50),
        default="Active"
    )


# =====================================================
# Conference Model
# =====================================================

class Conference(Base):
    __tablename__ = "conferences"

    conference_id = Column(Integer, primary_key=True, index=True)

    conference_name = Column(String(200), nullable=False)

    location = Column(String(200), nullable=False)

    conference_date = Column(String(100), nullable=False)

    publication_id = Column(
        Integer,
        ForeignKey("publications.publication_id"),
        nullable=False
    )