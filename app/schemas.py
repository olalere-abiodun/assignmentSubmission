from pydantic import BaseModel, ConfigDict, EmailStr
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    STUDENT = "student"
    LECTURER = "lecturer"
    ADMIN = "admin"

class UserBase(BaseModel):
    username: str

class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole



