from typing import Optional

from pydantic import EmailStr, BaseModel
from app.database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.security import hash_password, verify_password

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String)

    user_type_id = Column(Integer, ForeignKey('userType.id'))
    user_type = relationship("UserType", back_populates="users")

    student = relationship("Student", back_populates="user", uselist=False)
    

    def set_password(self, password: str):
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)


USER_TYPE = {
    "Student": 1,
    "Teacher": 2,
    "Admin": 3,
}

class UserType(Base):
    __tablename__ = 'userType'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    users = relationship("User", back_populates="user_type")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    
    class Config:
        from_attributes = True
