from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class AssignatureBase(BaseModel):
    name: str
    tag: str

class AssignatureResponse(AssignatureBase):
    id : int
    model_config = ConfigDict(from_attributes=True) # Es una conversión
    # Entre sqlalchemy y pydantic para evitar hacerlo manualmente.


class CurrentAssignaturesBase(BaseModel):
    student_id: int

class CurrentAssignaturesResponse(CurrentAssignaturesBase):
    id: int
    # Relación: lista de asignaturas
    assignatures: List[AssignatureResponse] = []
    model_config = ConfigDict(from_attributes=True)
