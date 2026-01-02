from sqlalchemy.orm import relationship
from app.database.database import Base
from sqlalchemy import Column, Integer, String, Table, ForeignKey


# Tabla intermedia many-to-many
current_assignature_assignature = Table(
    "current_assignature_assignature",
    Base.metadata,
    Column("current_assignature_id", Integer, ForeignKey("current_assignatures.id"), primary_key=True),
    Column("assignature_id", Integer, ForeignKey("assignature.id"), primary_key=True),
)

class Assignature(Base):
    __tablename__ = 'assignature'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    tag = Column(String)

    current_assignatures = relationship(
        "CurrentAssignatures",
        secondary=current_assignature_assignature,
        back_populates="assignatures"
    )


class CurrentAssignatures(Base):
    __tablename__ = 'current_assignatures'
    id = Column(Integer, primary_key=True, index=True)

# Relación many-to-many con Assignature
    assignatures = relationship(
        "Assignature",
        secondary=current_assignature_assignature,
        back_populates="current_assignatures"
    )

    # Relación one-to-many con Student
    student_id = Column(Integer, ForeignKey("student_info.id"))
    student = relationship("Student", back_populates="current_assignatures")
