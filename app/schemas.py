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
    User_id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole

class UserUpdate(UserBase):
    email: EmailStr
    full_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    role: UserRole

# Course Schema
class CourseBase(BaseModel):
    course_name: str
    course_code: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class RegisterCourse(CourseBase):
    pass

class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    course_code: Optional[str] = None
    description: Optional[str] = None

class CourseResponse(BaseModel):
    course_name: str
    course_code: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    






