from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database.database import get_db
from app.models.student import Student
from app.models.user import User
from app.routers.auth import  get_current_user
from app.schemas.assignature import AssignatureResponse
from app.models.assignature import CurrentAssignatures

student_router = APIRouter(prefix="/assignature", tags=["Student - Assignatures"], dependencies=[Depends(get_current_user)])


@student_router.get("/getMyCurrentsAssignatures/", response_model=List[AssignatureResponse])
async def get_all_current_assignature(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Validar que exista el estudiante

    result = await db.execute(select(Student).where(Student.user_id == user.id))
    student = result.scalars().first()

    if not student:
        raise HTTPException(status_code=404, detail="No existe el alumno")

    result_2 = await db.execute(
    select(CurrentAssignatures)
    .options(selectinload(CurrentAssignatures.assignatures))
    .where(CurrentAssignatures.student_id == student.id)
)    
    current_assignatures = result_2.scalars().all()

    if not current_assignatures:
        raise HTTPException(status_code=404, detail="No dispone de asignaturas")

    only_assignature = []

    for iter in current_assignatures:
        only_assignature.extend(iter.assignatures)

    return only_assignature

