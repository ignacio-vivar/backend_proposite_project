# schemas.py
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    user_id: int = Field(alias='id')
    email: EmailStr
    name: str

    class Config:
        orm_mode = True
        populate_by_name = True

class StudentWithUser(BaseModel):
    student_id: int = Field(alias='id')
    group: int
    year: int
    active: bool
    user: UserBase

    class Config:
        orm_mode = True
        populate_by_name = True

class StudentInfo(BaseModel):
    group: int
    year: int
    active: bool

    class Config:
        orm_mode = True



