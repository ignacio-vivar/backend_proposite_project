# routers/students.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.database.database import get_db
from app.models.user import User
from app.models.student import Student
from app.routers.auth import check_admin
from app.schemas.student import StudentInfo, StudentWithUser


admin_router = APIRouter(prefix="/admin", tags=["Admin - Student + UserInfo"], dependencies=[Depends(check_admin)])


@admin_router.get("/students", response_model=list[StudentWithUser])
async def get_students(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Student).options(selectinload(Student.user))
    )
    students_with_users = result.scalars().all()
    return students_with_users


@admin_router.get("/students/{id}", response_model=StudentWithUser)
async def get_student_by_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Student)
        .options(selectinload(Student.user))
        .where(Student.id == id)
    )
    student = result.scalars().first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student


@admin_router.post("/students/{user_id}", response_model=StudentWithUser)
async def add_student_data(user_id: int, data: StudentInfo, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Evitar duplicados - necesitamos cargar la relación student
    result_user_with_student = await db.execute(
        select(User)
        .options(selectinload(User.student))
        .where(User.id == user_id)
    )
    user_with_student = result_user_with_student.scalars().first()
    
    if user_with_student and user_with_student.student:
        raise HTTPException(status_code=400, detail="Student data already exists for this user")

    student = Student(
        user_id=user.id,
        group=data.group,
        year=data.year,
        active=data.active
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)

    # Recargar con la relación user
    result_final = await db.execute(
        select(Student)
        .options(selectinload(Student.user))
        .where(Student.id == student.id)
    )
    student_with_user = result_final.scalars().first()

    return student_with_user


@admin_router.patch("/students/disableSelecteds", response_model=dict)
async def disabled_student_select(select_users: List[int], db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User)
        .options(selectinload(User.student))
        .where(User.id.in_(select_users))
    )
    users_selected = result.scalars().all()

    if not users_selected:
        raise HTTPException(status_code=400, detail="There aren't any matches")
    
    names_output = []
    for u in users_selected:
        student = u.student

        names_output.append(u.name)

        print(u.name)
        if student:
            student.active = False

    await db.commit()

    return {"message": f"Disabled Students {names_output}"}


@admin_router.patch("/students/enableSelecteds", response_model=dict)
async def enabled_student_select(select_users: List[int], db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User)
        .options(selectinload(User.student))
        .where(User.id.in_(select_users))
    )
    users_selected = result.scalars().all()

    if not users_selected:
        raise HTTPException(status_code=400, detail="There aren't any matches")
    
    names_output = []

    for u in users_selected:
        student = u.student
        
        names_output.append(u.name)

        if student:
            student.active = True

    await db.commit()

    return {"message": f"Enable Students {names_output}"}


@admin_router.put("/students/{user_id}", response_model=StudentWithUser)
async def update_student_data(user_id: int, data: StudentInfo, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(User)
            .options(selectinload(User.student))
            .where(User.id == user_id)
        )
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.student:
            raise HTTPException(status_code=404, detail="Student data not found for this user")

        # Actualizar campos
        student = user.student
        student.group = data.group
        student.year = data.year
        student.active = data.active

        await db.commit()

        # Recargar con la relación
        result_final = await db.execute(
            select(Student)
            .options(selectinload(Student.user))
            .where(Student.id == student.id)
        )
        student_with_user = result_final.scalars().first()
        
        return student_with_user

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating student data: {str(e)}")
