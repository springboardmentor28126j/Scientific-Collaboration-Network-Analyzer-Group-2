from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.researcher import ResearcherProfile, ResearcherSkill, ResearcherInterest
from app.models.user import User
from app.repositories import researcher_repository
from app.utils.audit import write_audit_log


def create_profile(db: Session, current_user: User, data: dict) -> ResearcherProfile:
    if researcher_repository.get_by_user_id(db, current_user.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Researcher profile already exists")

    researcher = researcher_repository.create_researcher(db, user_id=current_user.user_id, **data)
    write_audit_log(
        db, user_id=current_user.user_id, action="CREATE", entity_type="researcher_profile",
        entity_id=researcher.researcher_id,
    )
    return researcher


def get_my_profile(db: Session, current_user: User) -> ResearcherProfile:
    researcher = researcher_repository.get_by_user_id(db, current_user.user_id)
    if researcher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Researcher profile not found")
    return researcher


def update_my_profile(db: Session, current_user: User, updates: dict) -> ResearcherProfile:
    researcher = get_my_profile(db, current_user)
    for field, value in updates.items():
        if value is not None:
            setattr(researcher, field, value)
    db.commit()
    db.refresh(researcher)
    write_audit_log(
        db, user_id=current_user.user_id, action="UPDATE", entity_type="researcher_profile",
        entity_id=researcher.researcher_id,
    )
    return researcher


def add_skill(db: Session, current_user: User, skill_name: str) -> ResearcherProfile:
    researcher = get_my_profile(db, current_user)
    skill = researcher_repository.get_or_create_skill(db, skill_name)

    already_linked = any(rs.skill_id == skill.skill_id for rs in researcher.skills)
    if not already_linked:
        db.add(ResearcherSkill(researcher_id=researcher.researcher_id, skill_id=skill.skill_id))
        db.commit()
        write_audit_log(
            db, user_id=current_user.user_id, action="UPDATE", entity_type="researcher_profile",
            entity_id=researcher.researcher_id, details=f"Added skill '{skill_name}'",
        )
    return researcher_repository.get_by_id(db, researcher.researcher_id)


def remove_skill(db: Session, current_user: User, skill_id: int) -> None:
    researcher = get_my_profile(db, current_user)
    link = next((rs for rs in researcher.skills if rs.skill_id == skill_id), None)
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not linked to this profile")
    db.delete(link)
    db.commit()
    write_audit_log(
        db, user_id=current_user.user_id, action="UPDATE", entity_type="researcher_profile",
        entity_id=researcher.researcher_id, details=f"Removed skill_id {skill_id}",
    )


def add_interest(db: Session, current_user: User, interest_name: str) -> ResearcherProfile:
    researcher = get_my_profile(db, current_user)
    interest = researcher_repository.get_or_create_interest(db, interest_name)

    already_linked = any(ri.interest_id == interest.interest_id for ri in researcher.interests)
    if not already_linked:
        db.add(ResearcherInterest(researcher_id=researcher.researcher_id, interest_id=interest.interest_id))
        db.commit()
        write_audit_log(
            db, user_id=current_user.user_id, action="UPDATE", entity_type="researcher_profile",
            entity_id=researcher.researcher_id, details=f"Added interest '{interest_name}'",
        )
    return researcher_repository.get_by_id(db, researcher.researcher_id)


def remove_interest(db: Session, current_user: User, interest_id: int) -> None:
    researcher = get_my_profile(db, current_user)
    link = next((ri for ri in researcher.interests if ri.interest_id == interest_id), None)
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interest not linked to this profile")
    db.delete(link)
    db.commit()
    write_audit_log(
        db, user_id=current_user.user_id, action="UPDATE", entity_type="researcher_profile",
        entity_id=researcher.researcher_id, details=f"Removed interest_id {interest_id}",
    )


def search(db: Session, department_id: int | None, skill_name: str | None, interest_name: str | None,
           page: int, page_size: int) -> list[ResearcherProfile]:
    return researcher_repository.search_researchers(
        db, department_id=department_id, skill_name=skill_name, interest_name=interest_name,
        page=page, page_size=page_size,
    )


def get_public_profile(db: Session, researcher_id: int) -> ResearcherProfile:
    researcher = researcher_repository.get_by_id(db, researcher_id)
    if researcher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Researcher not found")
    return researcher
