import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_institution_admin
from app.db.session import get_session
from app.models.institution import Department
from app.models.user import User
from app.schemas.institution import DepartmentCreate, DepartmentRead

router = APIRouter(prefix="/departments", tags=["Departments"])


async def get_department(session: AsyncSession, department_id: uuid.UUID, institution_id: uuid.UUID) -> Department:
    department = await session.scalar(select(Department).where(Department.id == department_id, Department.institution_id == institution_id))
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.get("", response_model=list[DepartmentRead])
async def list_departments(user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)):
    return (await session.scalars(select(Department).where(Department.institution_id == user.institution_id).order_by(Department.name))).all()


@router.post("", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
async def create_department(payload: DepartmentCreate, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)):
    department = Department(institution_id=user.institution_id, **payload.model_dump())
    session.add(department)
    await session.commit()
    await session.refresh(department)
    return department


@router.patch("/{department_id}", response_model=DepartmentRead)
async def update_department(department_id: uuid.UUID, payload: DepartmentCreate, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)):
    department = await get_department(session, department_id, user.institution_id)
    for field, value in payload.model_dump().items():
        setattr(department, field, value)
    await session.commit()
    await session.refresh(department)
    return department


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(department_id: uuid.UUID, user: User = Depends(require_institution_admin), session: AsyncSession = Depends(get_session)):
    await session.delete(await get_department(session, department_id, user.institution_id))
    await session.commit()
