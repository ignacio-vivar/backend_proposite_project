
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from sqlalchemy import select
from typing import List
from app.routers.auth import check_admin
from app.schemas.assignature import CurrentAssignaturesResponse
from app.models.assignature import Assignature, CurrentAssignatures
from app.models.student import Student
from sqlalchemy.orm import selectinload

router = APIRouter()

admin_router = APIRouter(prefix="/admin/assignature", tags=["Admin - Assignatures"], dependencies=[Depends(check_admin)])



@admin_router.get("/getStudentAssignatures/{student_id}", response_model=CurrentAssignaturesResponse)
async def get_student_assignatures(student_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CurrentAssignatures)
        .options(selectinload(CurrentAssignatures.assignatures))  # Carga eager de la relación
        .where(CurrentAssignatures.student_id == student_id)
    )
    current_assignatures = result.scalars().first()
    
    if current_assignatures is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron asignaturas para el estudiante con ID {student_id}"
        )
    
    return current_assignatures

# @admin_router.get("/getAllAssignature/", response_model=List[AssignatureResponse])
# async def get_all_assignature(db: AsyncSession = Depends(get_db)):
#
#     result = await db.execute(select(Assignature))
#     assignatures = result.scalars().all()
#
#     return assignatures

# @admin_router.post("/addAssignature/", response_model=AssignatureResponse)
# async def add_assignature(assignature: AssignatureBase, db: AsyncSession = Depends(get_db)):
#     new_assignature = Assignature(
#         name=assignature.name,
#         tag=assignature.tag  # ¡Faltaba esto!
#     )
#     db.add(new_assignature)
#     await db.commit()
#     await db.refresh(new_assignature)
#     return new_assignature
#


# Verifica que el estudiante exista, crea la tabla intermedia si no existe, busca la asignatura y si existe y no esta duplicada 
# Se agrega al estudiante en las asignaturas designadas.

# @admin_router.post("/student/{student_id}/addAssignature/{assignature_id}", response_model=CurrentAssignaturesResponse)
# async def add_assignature_to_student(student_id: int, assignature_id: int, db: AsyncSession = Depends(get_db)):
#     # Validar que exista el estudiante
#     result = await db.execute(
#         select(Student).where(Student.id == student_id)
#     )
#     student = result.scalars().first()
#     if not student:
#         raise HTTPException(status_code=404, detail="El estudiante no existe")
#
#     # Buscar la asignatura primero
#     result_3 = await db.execute(
#         select(Assignature).where(Assignature.id == assignature_id)
#     )
#     assignature = result_3.scalars().first()
#     if not assignature:
#         raise HTTPException(status_code=404, detail="La asignatura no existe")
#
#     # Buscar o crear el CurrentAssignatures (con selectinload)
#     result_2 = await db.execute(
#         select(CurrentAssignatures)
#         .options(selectinload(CurrentAssignatures.assignatures))
#         .where(CurrentAssignatures.student_id == student_id)
#     )
#     current = result_2.scalars().first()
#
#     if not current:
#         # Crear nuevo CurrentAssignatures con la asignatura
#         current = CurrentAssignatures(student_id=student_id)
#         current.assignatures.append(assignature)
#         db.add(current)
#         await db.commit()
#
#         # Recargar con selectinload
#         result_2 = await db.execute(
#             select(CurrentAssignatures)
#             .options(selectinload(CurrentAssignatures.assignatures))
#             .where(CurrentAssignatures.id == current.id)
#         )
#         current = result_2.scalars().first()
#     else:
#         # Evitar duplicados
#         if assignature not in current.assignatures:
#             current.assignatures.append(assignature)
#             await db.commit()
#
#             # Recargar con selectinload
#             result_2 = await db.execute(
#                 select(CurrentAssignatures)
#                 .options(selectinload(CurrentAssignatures.assignatures))
#                 .where(CurrentAssignatures.id == current.id)
#             )
#             current = result_2.scalars().first()
#
#     return current

@admin_router.post("/student/{student_id}/initAssignatures", response_model=CurrentAssignaturesResponse)
async def init_student_assignatures(student_id: int, db: AsyncSession = Depends(get_db)):
    # Verificar existencia del estudiante
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalars().first()

    if not student:
        raise HTTPException(status_code=404, detail="El estudiante no existe")

    # Verificar si ya tiene un CurrentAssignatures
    result_2 = await db.execute(
        select(CurrentAssignatures).where(
            CurrentAssignatures.student_id == student_id
        )
    )
    existing = result_2.scalars().first()    

    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un registro de asignaturas para este estudiante")

    # Crear relación vacía
    current = CurrentAssignatures(student_id=student_id)
    db.add(current)
    await db.commit()
    await db.refresh(current)

    return current


@admin_router.put("/student/{student_id}/assignatures", response_model=CurrentAssignaturesResponse)
async def update_student_assignatures(student_id: int, assignature_ids: List[int], db: AsyncSession = Depends(get_db)):
    # Verificar existencia del estudiante
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="El estudiante no existe")
    
    # Buscar CurrentAssignatures CON selectinload
    result_2 = await db.execute(
        select(CurrentAssignatures)
        .options(selectinload(CurrentAssignatures.assignatures))
        .where(CurrentAssignatures.student_id == student_id)
    )
    current = result_2.scalars().first()
    
    # Guardar el ID antes de cualquier operación
    current_id = None
    
    if not current:
        # Crear nuevo
        current = CurrentAssignatures(student_id=student_id)
        db.add(current)
        await db.commit()
        current_id = current.id  # Guardar el ID después del commit
    else:
        current_id = current.id  # Ya tenemos el ID
    
    # Obtener todas las asignaturas válidas
    result_3 = await db.execute(
        select(Assignature).where(Assignature.id.in_(assignature_ids))
    )
    valid_assignatures = result_3.scalars().all()
    
    # Recargar current con selectinload usando el ID guardado
    result_reload = await db.execute(
        select(CurrentAssignatures)
        .options(selectinload(CurrentAssignatures.assignatures))
        .where(CurrentAssignatures.id == current_id)
    )
    current = result_reload.scalars().first()
    
    if not current:
        raise HTTPException(status_code=500, detail="Error al cargar CurrentAssignatures")
    
    # Actualizar la relación
    current.assignatures = valid_assignatures
    await db.commit()
    
    # Recargar una última vez para retornar
    result_final = await db.execute(
        select(CurrentAssignatures)
        .options(selectinload(CurrentAssignatures.assignatures))
        .where(CurrentAssignatures.id == current_id)
    )
    current = result_final.scalars().first()
    
    return current

# @admin_router.delete("/deleteAssignature/{id_assignature}", response_model=str)
# async def delete_assignature(id_assignature : int, db: AsyncSession = Depends((get_db))):
#
#     result = await db.execute(
#         select(Assignature).where(Assignature.id == id_assignature)
#     )
#     assign_del = result.scalars().first()
#
#     if assign_del is None:
#         raise HTTPException(status_code=404, detail="No existe la asignatura")
#
#     name = assign_del.name
#
#     await db.delete(assign_del)
#     await db.commit()
#     return f"Se ha eliminado la asignatura : {name}"
