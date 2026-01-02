# schemas.py
from pydantic import BaseModel, Field
from datetime import date

from app.models.grade import Status, Toe

class TaskCreate(BaseModel):
    description: str
    deadtime: date
    type_of_evaluation: Toe
    assignature_id: int


class TaskUpdate(BaseModel):
    description: str
    deadtime: date
    type_of_evaluation: Toe  # o el enum Toe si preferís
    
    class Config:
        orm_mode = True
        populate_by_name = True


class TaskBase(BaseModel):
    task_id: int = Field(alias='id')
    description: str
    deadtime: date
    type_of_evaluation: Toe  # o el enum Toe si preferís
    
    class Config:
        orm_mode = True
        populate_by_name = True


class SubmissionWithTask(BaseModel):
    submission_id: int = Field(alias='id')
    grade: float | None
    observation: str | None
    status: Status  # o el enum Status si preferís
    submitted_at: date | None
    graded_at: date | None
    task: TaskBase
    
    class Config:
        orm_mode = True
        populate_by_name = True


class SubmissionStudentData(BaseModel):
    submission_id: int = Field(alias='id')
    grade: float | None
    observation: str | None
    status: Status  # o el enum Status si preferís
    task: TaskBase
    
    class Config:
        orm_mode = True
        populate_by_name = True




class SubmissionWithStudentAndTask(SubmissionWithTask):
    student: dict  # {id, name, group, year}
    
class SubmissionMini(BaseModel):
    submission_id: int = Field(alias='id')
    grade: float | None
    observation: str | None
    status: Status  # o el enum Status si preferís
    task_name: str
    student_name: str

class SubmissionUpdate(BaseModel):
    grade: float | None = None
    observation: str | None = None
    status: Status | None = None
