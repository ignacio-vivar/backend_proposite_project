
from fastapi import APIRouter, Depends, HTTPException
from app.database.database import get_db
from sqlalchemy.orm import Session
from typing import List
from app.routers.auth import check_admin
from app.schemas.assignature import AssignatureBase, AssignatureResponse, CurrentAssignaturesResponse, CurrentAssignaturesBase
from app.models.assignature import Assignature, CurrentAssignatures
from app.models.student import Student

router = APIRouter()

admin_router = APIRouter(prefix="/admin/assignature", tags=["Admin - Assignatures"], dependencies=[Depends(check_admin)])


@admin_router.get("/getStudentAssignatures/{student_id}", response_model=CurrentAssignaturesResponse)
def get_student_assignatures(student_id: int, db: Session = Depends(get_db)):
    current_assignatures = db.query(CurrentAssignatures).filter(CurrentAssignatures.student_id == student_id).first()
    return current_assignatures

@admin_router.get("/getAllAssignature/", response_model=List[AssignatureResponse])
def get_all_assignature(db: Session = Depends(get_db)):

    assignatures = db.query(Assignature).all()
    return assignatures

@admin_router.post("/addAssignature/", response_model=AssignatureResponse)
def add_assignature(assignature: AssignatureBase ,db: Session = Depends(get_db)):
    new_assignature = Assignature(name = assignature.name)
    db.add(new_assignature)
    db.commit()
    db.refresh(new_assignature)
    return new_assignature

@router.get("/getMyCurrentsAssignatures/", response_model=List[CurrentAssignaturesResponse])
def get_all_current_assignature(db: Session = Depends(get_db)):
    # Validar que exista el estudiante
    current_assignatures = db.query(CurrentAssignatures).all()
    if not current_assignatures:
        raise HTTPException(status_code=404, detail="No dispone de asignaturas")

    
    return current_assignatures


# Verifica que el estudiante exista, crea la tabla intermedia si no existe, busca la asignatura y si existe y no esta duplicada 
# Se agrega al estudiante en las asignaturas designadas.

@admin_router.post("/student/{student_id}/addAssignature/{assignature_id}", response_model=CurrentAssignaturesResponse)
def add_assignature_to_student(student_id: int, assignature_id: int, db: Session = Depends(get_db)):
    # Validar que exista el estudiante
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="El estudiante no existe")

    # Buscar o crear el CurrentAssignatures
    current = db.query(CurrentAssignatures).filter(CurrentAssignatures.student_id == student_id).first()
    if not current:
        current = CurrentAssignatures(student_id=student_id)
        db.add(current)
        db.commit()
        db.refresh(current)

    # Buscar la asignatura
    assignature = db.query(Assignature).filter(Assignature.id == assignature_id).first()
    if not assignature:
        raise HTTPException(status_code=404, detail="La asignatura no existe")

    # Evitar duplicados
    if assignature not in current.assignatures:
        current.assignatures.append(assignature)
        db.commit()
        db.refresh(current)

    return current


@admin_router.post("/student/{student_id}/initAssignatures", response_model=CurrentAssignaturesResponse)
def init_student_assignatures(student_id: int, db: Session = Depends(get_db)):
    # Verificar existencia del estudiante
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="El estudiante no existe")

    # Verificar si ya tiene un CurrentAssignatures
    existing = db.query(CurrentAssignatures).filter(CurrentAssignatures.student_id == student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un registro de asignaturas para este estudiante")

    # Crear relación vacía
    current = CurrentAssignatures(student_id=student_id)
    db.add(current)
    db.commit()
    db.refresh(current)

    return current

@admin_router.put("/student/{student_id}/assignatures", response_model=CurrentAssignaturesResponse)
def update_student_assignatures(student_id: int, assignature_ids: List[int], db: Session = Depends(get_db)):
    # Verificar existencia del estudiante
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="El estudiante no existe")

    # Buscar o crear el CurrentAssignatures
    current = db.query(CurrentAssignatures).filter(CurrentAssignatures.student_id == student_id).first()
    if not current:
        current = CurrentAssignatures(student_id=student_id)
        db.add(current)
        db.commit()
        db.refresh(current)

    # Obtener todas las asignaturas válidas que existan en DB
    valid_assignatures = db.query(Assignature).filter(Assignature.id.in_(assignature_ids)).all()

    # Actualizar la relación: borrar las anteriores y poner solo las nuevas
    current.assignatures = valid_assignatures

    db.commit()
    db.refresh(current)

    return current

@router.get("/getAssignature/{id}", response_model=AssignatureResponse)
def get_assignature(id: int, db:Session = Depends(get_db)):
    assignature = db.query(Assignature).filter(Assignature.id == id).first(
    )

    if not assignature:
        raise HTTPException(status_code=404, detail="No existe la asignatura solicitada")
    
    return assignature


@admin_router.delete("/deleteAssignature/{id_assignature}", response_model=str)
def delete_assignature(id_assignature : int, db: Session = Depends((get_db))):
    assign_del = db.query(Assignature).filter(Assignature.id == id_assignature).first()

    if assign_del is None:
        raise HTTPException(status_code=404, detail="No existe la asignatura")

    name = assign_del.name

    db.delete(assign_del)
    db.commit()
    return f"Se ha eliminado la asignatura : {name}"
