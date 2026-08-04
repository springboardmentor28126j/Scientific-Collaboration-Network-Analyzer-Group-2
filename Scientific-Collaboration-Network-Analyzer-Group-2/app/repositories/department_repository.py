from uuid import UUID

from sqlalchemy.orm import Session

from app.models.department import Department


class DepartmentRepository:

    @staticmethod
    def create(db: Session, department: Department):
        db.add(department)
        db.commit()
        db.refresh(department)
        return department

    @staticmethod
    def get_all(db: Session):
        return db.query(Department).all()

    @staticmethod
    def get_by_id(db: Session, department_id: UUID):
        return (
            db.query(Department)
            .filter(Department.id == department_id)
            .first()
        )

    @staticmethod
    def delete(db: Session, department: Department):
        db.delete(department)
        db.commit()
