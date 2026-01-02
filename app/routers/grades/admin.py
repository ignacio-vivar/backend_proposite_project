from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from sqlalchemy.orm.attributes import set_attribute
from app.database.database import get_db
from app.models.user import User
from app.routers.auth import check_admin
from app.models.grade import Tasks, TaskSubmission, Toe, Status
from app.models.student import Student
from app.models.assignature import CurrentAssignatures, current_assignature_assignature
from app.schemas.task_student import SubmissionMini, SubmissionUpdate, SubmissionWithStudentAndTask, TaskBase, TaskCreate, TaskUpdate

admin_router = APIRouter(
    prefix="/admin", 
    tags=["Admin - Grades and Assigments"], 
    dependencies=[Depends(check_admin)]
)


@admin_router.put("/tasks_update/{id_task}")
def update_tasks(id_task: int, task_base: TaskUpdate, db: Session = Depends(get_db)):
    try:
        task = db.query(Tasks).filter(Tasks.id == id_task).first()
        if not task:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")

        update_data = task_base.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(task, field):
                set_attribute(task, field, value)
        db.commit()
        db.refresh(task)
        
        return "Update Ok"
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating task data: {str(e)}")


@admin_router.delete("/tasks_delete/{id_task}")
def delete_tasks(id_task: int, db: Session = Depends(get_db)):
        task = db.query(Tasks).filter(Tasks.id == id_task).first()

        if not task:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")

        db.delete(task)        
        db.commit()
        
        return "Delete Ok"



# Función helper para sincronizar (reutilizable)
def sync_submissions_for_assignature(assignature_id: int, db: Session):
    """
    Sincroniza submissions: crea faltantes y elimina huérfanas
    """
    # 1. Obtener tasks de la materia
    tasks = db.query(Tasks).filter(Tasks.assignature_id == assignature_id).all()
    task_ids = [task.id for task in tasks]
    
    # 2. Obtener estudiantes activos de la materia
    students = db.query(Student)\
        .join(CurrentAssignatures, Student.id == CurrentAssignatures.student_id)\
        .join(
            current_assignature_assignature,
            CurrentAssignatures.id == current_assignature_assignature.c.current_assignature_id
        )\
        .filter(
            current_assignature_assignature.c.assignature_id == assignature_id,
            Student.active == True
        ).all()
    student_ids = [student.id for student in students]
    
    # 3. LIMPIAR submissions huérfanas
    if task_ids:
        # Eliminar submissions de estudiantes que ya no cursan
        if student_ids:
            db.query(TaskSubmission)\
                .filter(TaskSubmission.task_id.in_(task_ids))\
                .filter(~TaskSubmission.student_id.in_(student_ids))\
                .delete(synchronize_session=False)
        else:
            # Si no hay estudiantes, eliminar todas las submissions de la materia
            db.query(TaskSubmission)\
                .filter(TaskSubmission.task_id.in_(task_ids))\
                .delete(synchronize_session=False)
    
    # 4. CREAR submissions faltantes
    for student in students:
        for task in tasks:
            existing = db.query(TaskSubmission).filter(
                TaskSubmission.student_id == student.id,
                TaskSubmission.task_id == task.id
            ).first()
            
            if not existing:
                submission = TaskSubmission(
                    student_id=student.id,
                    task_id=task.id,
                    status=Status.UNDONE
                )
                db.add(submission)
    
    db.commit()# GET actualizado

@admin_router.get("/tasks/{assignature_id}/submissions", response_model=List[SubmissionWithStudentAndTask])
def get_submissions_by_assignature(assignature_id: int, db: Session = Depends(get_db)):
    # 1. Sincronizar primero
    sync_submissions_for_assignature(assignature_id, db)
    
    # 2. Luego hacer el query normal
    submissions = db.query(TaskSubmission)\
        .join(Tasks, TaskSubmission.task_id == Tasks.id)\
        .join(Student, TaskSubmission.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .options(
            joinedload(TaskSubmission.task),
            joinedload(TaskSubmission.student).joinedload(Student.user)
        )\
        .filter(
            Tasks.assignature_id == assignature_id,
            Student.active == True  # Solo estudiantes activos
        )\
        .all()
    
    result = []
    for sub in submissions:
        result.append({
            "id": sub.id,
            "grade": sub.grade,
            "observation": sub.observation,
            "status": sub.status,
            "submitted_at": sub.submitted_at,
            "graded_at": sub.graded_at,
            "student": {
                "id": sub.student.id,
                "name": sub.student.user.name,
                "group": sub.student.group,
                "year": sub.student.year
            },
            "task": sub.task
        })
    
    return result


@admin_router.get("/tasks/grades_list/{assignature_id}/", response_model=List[SubmissionMini])
def get_grades_by_assignature(assignature_id: int, db: Session = Depends(get_db)):
    # 1. Sincronizar primero
    sync_submissions_for_assignature(assignature_id, db)
    
    # 2. Luego hacer el query normal
    submissions = db.query(TaskSubmission)\
        .join(Tasks, TaskSubmission.task_id == Tasks.id)\
        .join(Student, TaskSubmission.student_id == Student.id)\
        .join(User, Student.user_id == User.id)\
        .options(
            joinedload(TaskSubmission.task),
            joinedload(TaskSubmission.student).joinedload(Student.user)
        )\
        .filter(
            Tasks.assignature_id == assignature_id,
            Student.active == True  # Solo estudiantes activos
        )\
        .all()
    
    result = []
    for sub in submissions:
        result.append({
            "id": sub.id,
            "grade": sub.grade,
            "observation": sub.observation,
            "status": sub.status,
            "task_name": sub.task.description,
            "student_name": sub.student.user.name,
        })
    
    return result

# Endpoint PUT
@admin_router.put("/submissions/{submission_id}")
def update_submission(
    submission_id: int, 
    data: SubmissionUpdate, 
    db: Session = Depends(get_db)
):
    submission = db.query(TaskSubmission).filter(TaskSubmission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission no encontrada")
    
    # Actualizar solo los campos que vienen en el request
    if data.grade is not None:
        submission.grade = data.grade # type: ignore
    if data.observation is not None:
        submission.observation = data.observation # type: ignore
    if data.status is not None:
        submission.status = data.status # type: ignore
        # Auto-setear fecha de calificación si se aprueba/desaprueba
        if data.status in [Status.PASSED, Status.FAILED]:
            submission.graded_at = date.today() # type: ignore
    
    db.commit()
    db.refresh(submission)
    
    return {
        "message": "Calificación actualizada",
    }


# POST simplificado (reutiliza la lógica)
@admin_router.post("/tasks")
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    new_task = Tasks(
        description=task_data.description,
        deadtime=task_data.deadtime,
        type_of_evaluation=task_data.type_of_evaluation,
        assignature_id=task_data.assignature_id
    )
    db.add(new_task)
    db.commit()
    
    # Sincronizar submissions (crea para todos los estudiantes)
    sync_submissions_for_assignature(task_data.assignature_id, db)
    
    students_count = db.query(Student)\
        .join(CurrentAssignatures, Student.id == CurrentAssignatures.student_id)\
        .join(
            current_assignature_assignature,
            CurrentAssignatures.id == current_assignature_assignature.c.current_assignature_id
        )\
        .filter(
            current_assignature_assignature.c.assignature_id == task_data.assignature_id,
            Student.active == True
        ).count()
    
    return {"message": "Tarea creada exitosamente"}

@admin_router.get("/tasks/mindata/{assignature_id}", response_model=List[TaskBase])
def get_task_data_by_assignature(assignature_id: int, db: Session = Depends(get_db)):
    tasks = db.query(Tasks)\
         .filter(Tasks.assignature_id == assignature_id).order_by(Tasks.id.desc()).all()  
    # Formatear para incluir info del estudiante
       
    return tasks
