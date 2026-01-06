
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload
from app.database.database import get_db
from app.models.student import Student
from app.models.user import User
from app.routers.auth import get_current_user

from app.models.grade import TaskSubmission, Tasks
from app.schemas.task_student import SubmissionStudentData, SubmissionWithTask

student_router = APIRouter(prefix="/student", tags=["Students Califications"])


# @student_router.get("/getStudentCalifications/", response_model=List[SubmissionStudentData])
# async def get_califications_min(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
#     # Obtener el student asociado al user
#     result = await db.execute(
#         select(Student).where(Student.user_id == user.id)
#     )
#     student = result.scalars().first()
#
#     if not student:
#         raise HTTPException(status_code=404, detail="Usuario no es estudiante")
#
#     # Obtener submissions con selectinload para cargar la relación task
#     result_works = await db.execute(
#         select(TaskSubmission)
#         .options(selectinload(TaskSubmission.task))
#         .where(TaskSubmission.student_id == student.id)
#     )
#     user_works = result_works.scalars().all()
#
#     # Validar integridad de datos
#     for work in user_works:
#         if work.task is None:
#             raise HTTPException(
#                 status_code=500, 
#                 detail=f"Datos corruptos: Submission {work.id} sin task asociado"
#             )
#
#     return user_works

@student_router.get("/getStudentCalificationsByAssignature/{assignature_id}", response_model=List[SubmissionStudentData])
async def get_califications_min_by_assignature(
    assignature_id: int, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # Obtener el student asociado al user
    result = await db.execute(
        select(Student).where(Student.user_id == user.id)
    )
    student = result.scalars().first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Usuario no es estudiante")
    
    # Obtener submissions con join y selectinload
    result_works = await db.execute(
        select(TaskSubmission)
        .join(TaskSubmission.task)
        .options(selectinload(TaskSubmission.task))
        .where(
            TaskSubmission.student_id == student.id,
            Tasks.assignature_id == assignature_id
        )
    )
    user_works = result_works.scalars().all()
    
    # Validar integridad de datos
    for work in user_works:
        if work.task is None:
            raise HTTPException(
                status_code=500, 
                detail=f"Datos corruptos: Submission {work.id} sin task asociado"
            )
    
    return user_works
