from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl
from enum import Enum
from typing import Optional
from datetime import datetime, date, timedelta

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

class EnrollResponse(BaseModel):
    username: str
    course_name: str
    course_code: str
    lecturer_id: int

class AssignmentCreate(BaseModel):
    course_id: int
    assignment_title: str
    description: Optional[str] = None
    due_date: datetime

    model_config = ConfigDict(from_attributes=True)

class AssignmentResponse(BaseModel):
    assignment_id: int
    assignment_title: str
    description: Optional[str] = None
    due_date: datetime

class AssignmentUpdate(BaseModel):
    assignment_title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class SubmissionCreate(BaseModel):
    assignment_id: int                       
    student_id: int                          
    content: str                             
    file_url: Optional[str] = None        
    submission_date: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class SubmissionResponse(BaseModel):
    submission_id: int
    assignment_id: int
    user_id: int
    submission_date: datetime

    model_config = ConfigDict(from_attributes=True)

class AllSubmissionsResponse(BaseModel):
    submission_id: int
    assignment_id: int
    user_id: int
    content: str
    file_url: Optional[str]
    submission_date: datetime

    model_config = ConfigDict(from_attributes=True)


    






