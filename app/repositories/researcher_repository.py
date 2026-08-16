from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.researcher import (
    ResearcherProfile,
    Skill,
    ResearcherSkill,
    ResearchInterest,
    ResearcherInterest,
)


def get_by_user_id(db: Session, user_id: int) -> ResearcherProfile | None:
    query = (
        select(ResearcherProfile)
        .options(
            joinedload(ResearcherProfile.skills).joinedload(ResearcherSkill.skill),
            joinedload(ResearcherProfile.interests).joinedload(ResearcherInterest.interest),
        )
        .where(ResearcherProfile.user_id == user_id)
    )
    return db.scalar(query)


def get_by_id(db: Session, researcher_id: int) -> ResearcherProfile | None:
    query = (
        select(ResearcherProfile)
        .options(
            joinedload(ResearcherProfile.skills).joinedload(ResearcherSkill.skill),
            joinedload(ResearcherProfile.interests).joinedload(ResearcherInterest.interest),
        )
        .where(ResearcherProfile.researcher_id == researcher_id)
    )
    return db.scalar(query)


def search_researchers(
    db: Session,
    department_id: int | None = None,
    skill_name: str | None = None,
    interest_name: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> list[ResearcherProfile]:
    query = select(ResearcherProfile).distinct()

    if department_id is not None:
        query = query.where(ResearcherProfile.department_id == department_id)
    if skill_name is not None:
        query = query.join(ResearcherSkill).join(Skill).where(Skill.name.ilike(f"%{skill_name}%"))
    if interest_name is not None:
        query = query.join(ResearcherInterest).join(ResearchInterest).where(
            ResearchInterest.name.ilike(f"%{interest_name}%")
        )

    query = query.offset((page - 1) * page_size).limit(page_size)
    return list(db.scalars(query).unique().all())


def create_researcher(db: Session, **kwargs) -> ResearcherProfile:
    researcher = ResearcherProfile(**kwargs)
    db.add(researcher)
    db.commit()
    db.refresh(researcher)
    return researcher


def get_or_create_skill(db: Session, name: str) -> Skill:
    skill = db.scalar(select(Skill).where(Skill.name == name))
    if skill is None:
        skill = Skill(name=name)
        db.add(skill)
        db.commit()
        db.refresh(skill)
    return skill


def get_or_create_interest(db: Session, name: str) -> ResearchInterest:
    interest = db.scalar(select(ResearchInterest).where(ResearchInterest.name == name))
    if interest is None:
        interest = ResearchInterest(name=name)
        db.add(interest)
        db.commit()
        db.refresh(interest)
    return interest
