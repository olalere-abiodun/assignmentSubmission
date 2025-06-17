from sqlalchemy import Column, String, Integer, ForeignKey, Enum, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database import Base


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(255),nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    courses = relationship("Course", back_populates="lecturer")
    enrollments = relationship("Enrollment", back_populates="user")
    assignments = relationship("Assignment", back_populates="lecturer")

class Course(Base):
    __tablename__ = 'courses'

    course_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_name = Column(String(255), nullable=False)
    course_code = Column(String(50), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    lecturer_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    lecturer = relationship("Users", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")

# Student Enrollment Model
class Enrollment(Base):
    __tablename__ = 'enrollments'

    enrollment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.course_id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("Users", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

# Assignment Model
class Assignment(Base):
    __tablename__ = 'assignments'

    assignment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.course_id'), nullable=False)
    lecturer_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    assignment_title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    due_date = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    course = relationship("Course", back_populates="assignments")
    lecturer = relationship("Users", back_populates="assignments")

