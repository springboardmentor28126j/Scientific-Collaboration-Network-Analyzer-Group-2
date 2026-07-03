from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Collaboration(Base):
    __tablename__ = "collaborations"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    institution_a = Column(String)
    institution_b = Column(String)
    description = Column(String)

class ProjectAssignment(Base):
    __tablename__ = "project_assignments"

    id = Column(Integer, primary_key=True, index=True)
    collaboration_id = Column(Integer, ForeignKey("collaborations.id"))
    researcher_id = Column(Integer, ForeignKey("researchers.id"))
    role_in_project = Column(String)
