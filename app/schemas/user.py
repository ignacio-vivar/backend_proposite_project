from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    email: EmailStr  
    name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserResponseName(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)
