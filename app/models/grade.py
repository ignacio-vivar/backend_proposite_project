from sqlalchemy.orm import relationship
from app.database.database import Base
from sqlalchemy import Column, Date, Float, Integer, String, ForeignKey
from sqlalchemy import Enum
from enum import Enum as PyEnum

class Toe(PyEnum):
    TP = "trabajo-practico"
    FORM = "formulario"
    TEST = "evaluación"

class Status(PyEnum):
    UNDONE = "sin-entregar"
    DONE = "entregado"
    FAILED = "desaprobado"
    PASSED = "aprobado"
    REDO = "rehacer"

class Tasks(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    deadtime = Column(Date)
    type_of_evaluation =  Column(Enum(Toe), nullable=True)
    assignature_id = Column(Integer, ForeignKey("assignature.id"))
    submissions = relationship("TaskSubmission", back_populates="task", cascade="all, delete-orphan")

class TaskSubmission(Base):
    __tablename__ = 'task_submissions'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_info.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    
    grade = Column(Float, nullable=True)
    observation = Column(String, nullable=True)  # markdown
    status = Column(Enum(Status), default=Status.UNDONE, nullable=True)  # sin_entregar, entregado, aprobado, desaprobado
    submitted_at = Column(Date, nullable=True)
    graded_at = Column(Date, nullable=True)
    
    # Relaciones (igual que hiciste con User y Student)
    student = relationship("Student", back_populates="submissions")
    task = relationship("Tasks", back_populates="submissions")
