from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.researcher import (
    ResearcherCreate,
    ResearcherUpdate,
    ResearcherOut,
    SkillAdd,
    InterestAdd,
)
from app.services import researcher_service

router = APIRouter(prefix="/researchers", tags=["Researchers"])


@router.post("", response_model=ResearcherOut, status_code=201)
def create_my_researcher_profile(
    payload: ResearcherCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return researcher_service.create_profile(db, current_user, payload.model_dump())


@router.get("/me", response_model=ResearcherOut)
def get_my_researcher_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return researcher_service.get_my_profile(db, current_user)


@router.patch("/me", response_model=ResearcherOut)
def update_my_researcher_profile(
    payload: ResearcherUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return researcher_service.update_my_profile(db, current_user, payload.model_dump(exclude_unset=True))


@router.get("", response_model=list[ResearcherOut])
def search_researchers(
    department_id: int | None = None,
    skill: str | None = None,
    interest: str | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return researcher_service.search(db, department_id, skill, interest, page, page_size)


@router.get("/{researcher_id}", response_model=ResearcherOut)
def get_researcher(researcher_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return researcher_service.get_public_profile(db, researcher_id)


@router.post("/me/skills", response_model=ResearcherOut, status_code=status.HTTP_201_CREATED)
def add_skill(payload: SkillAdd, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return researcher_service.add_skill(db, current_user, payload.name)


@router.delete("/me/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_skill(skill_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    researcher_service.remove_skill(db, current_user, skill_id)
    return None


@router.post("/me/interests", response_model=ResearcherOut, status_code=status.HTTP_201_CREATED)
def add_interest(payload: InterestAdd, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return researcher_service.add_interest(db, current_user, payload.name)


@router.delete("/me/interests/{interest_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_interest(interest_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    researcher_service.remove_interest(db, current_user, interest_id)
    return None
