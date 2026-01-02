from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.database.database import get_db
from sqlalchemy.orm import Session
from app.models.student import Student
from app.models.user import User
from app.routers.auth import  get_current_user
from app.schemas.assignature import AssignatureResponse, CurrentAssignaturesResponse
from app.models.assignature import Assignature, CurrentAssignatures

student_router = APIRouter(prefix="/assignature", tags=["Student - Assignatures"], dependencies=[Depends(get_current_user)])



@student_router.get("/getAssignature/{id}", response_model=AssignatureResponse)
def get_assignature(id: int, db:Session = Depends(get_db)):
    assignature = db.query(Assignature).filter(Assignature.id == id).first(
    )

    if not assignature:
        raise HTTPException(status_code=404, detail="No existe la asignatura solicitada")
    
    return assignature


@student_router.get("/getMyCurrentsAssignatures/", response_model=List[AssignatureResponse])
def get_all_current_assignature(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validar que exista el estudiante

    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="No existe el alumno")

    current_assignatures = db.query(CurrentAssignatures).filter(CurrentAssignatures.student_id == student.id).all()
    if not current_assignatures:
        raise HTTPException(status_code=404, detail="No dispone de asignaturas")

    only_assignature = []

    for iter in current_assignatures:
        only_assignature.extend(iter.assignatures)

    return only_assignature

