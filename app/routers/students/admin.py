# routers/students.py
from typing import List
from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database.database import get_db
from app.models.user import User
from app.models.student import Student
from app.routers.auth import check_admin
from app.schemas.student import StudentInfo, StudentWithUser


admin_router = APIRouter(prefix="/admin", tags=["Admin - Student + UserInfo"], dependencies=[Depends(check_admin)])


@admin_router.get("/students", response_model=list[StudentWithUser])
def get_students(db: Session = Depends(get_db)):
    students_with_users = db.query(Student).options(joinedload(Student.user)).all()
    return students_with_users


@admin_router.get("/students/{id}", response_model=StudentWithUser)
def get_student_by_id(id: int, db: Session = Depends(get_db)):
    student = db.query(Student).options(joinedload(Student.user)).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student

@admin_router.post("/students/{user_id}", response_model=StudentWithUser)
def add_student_data(user_id: int, data: StudentInfo, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Evitar duplicados
    if user.student:
        raise HTTPException(status_code=400, detail="Student data already exists for this user")

    student = Student(
        user_id=user.id,
        group=data.group,
        year=data.year,
        active=data.active
    )
    db.add(student)
    db.commit()
    db.refresh(user)  # refresca para que traiga la relación


    student_with_user = db.query(Student).options(joinedload(Student.user)).filter(Student.id == student.id).first()

    return student_with_user

@admin_router.patch("/students/disableSelecteds", response_model=dict)
def disabled_student_select(select_users: List[int], db: Session = Depends(get_db)):

    users_selected = (db.query(User)
                      .options(joinedload(User.student))
                      .filter(User.id.in_(select_users)).all())

    if not users_selected:
        raise HTTPException(status_code=400, detail="There aren't any matches")
    
    names_output = []
    for u in users_selected:
        student = u.student

        names_output.append(u.name)

        print(u.name)
        if student:
           student.active = False

    db.commit()

    return {"message" : f"Disabled Students {names_output}"}


@admin_router.patch("/students/enableSelecteds", response_model=dict)
def enabled_student_select(select_users: List[int], db: Session = Depends(get_db)):

    users_selected = (db.query(User)
                      .options(joinedload(User.student))
                      .filter(User.id.in_(select_users)).all())

    if not users_selected:
        raise HTTPException(status_code=400, detail="There aren't any matches")
    
    names_output = []

    for u in users_selected:
        student = u.student
        
        names_output.append(u.name)

        if student:
           student.active = True

    db.commit()

    return {"message" : f"Enable Students {names_output}"}

@admin_router.put("/students/{user_id}", response_model=StudentWithUser)
def update_student_data(user_id: int, data: StudentInfo, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.student:
            raise HTTPException(status_code=404, detail="Student data not found for this user")

        # Actualizar campos
        student = user.student
        student.group = data.group
        student.year = data.year
        student.active = data.active

        db.commit()
        db.refresh(user)

        student_with_user = db.query(Student).options(joinedload(Student.user)).filter(Student.id == student.id).first()
        return student_with_user

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating student data: {str(e)}")
