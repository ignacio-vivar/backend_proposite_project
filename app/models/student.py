from sqlalchemy.orm import relationship
from app.database.database import Base
from sqlalchemy import Boolean, Column, Integer, ForeignKey

class Student(Base):
    __tablename__ = 'student_info'

    id = Column(Integer, primary_key=True, index=True)
    group = Column(Integer)
    year = Column(Integer)
    active = Column(Boolean)

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="student")

    current_assignatures = relationship("CurrentAssignatures", back_populates="student")

    submissions = relationship("TaskSubmission", back_populates="student")
