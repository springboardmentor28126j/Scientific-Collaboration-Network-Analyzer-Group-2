from sqlalchemy.orm import Session
from app.models.publication import Publication, PublicationStatus

def get_publications_by_status(db: Session, status: PublicationStatus):
    return db.query(Publication).filter(Publication.status == status).all()

def get_publications_by_author(db: Session, author_id: int):
    return db.query(Publication).filter(Publication.author_id == author_id).all()

def change_status(db: Session, publication_id: int, new_status: PublicationStatus):
    pub = db.query(Publication).filter(Publication.id == publication_id).first()
    if pub:
        pub.status = new_status
        db.commit()
        db.refresh(pub)
    return pub
