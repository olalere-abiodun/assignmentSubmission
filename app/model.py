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

    courses = relationship("Course", back_populates="user")

class Course(Base):
    __tablename__ = 'courses'

    course_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_name = Column(String(255), nullable=False)
    course_code = Column(String(50), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    lecturer_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("Users", back_populates="courses")

