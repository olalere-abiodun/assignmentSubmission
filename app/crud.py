from fastapi import HTTPException
from sqlalchemy.orm import Session
import schemas, model

#User CRUD
# ==========================================================
# Create User
def Sign_up(db: Session, user: schemas.UserCreate, hashed_password: str):
   db_user = model.Users (
        full_name = user.full_name,
        email = user.email,
        username = user.username,
        hashed_password = hashed_password,
        role = user.role
   )
   db.add(db_user)
   db.commit()
   db.refresh(db_user)
   return db_user

# Get User by Email
def check_email(db: Session, email:str):
   return db.query(model.Users).filter(model.Users.email == email).first()

# Check for Username Exist
def check_username(db: Session, username:str):
   return db.query(model.Users).filter(model.Users.username == username).first()

#Edit User Profile
def UpdateUser(db: Session, email:str, updateUser: schemas.UserUpdate):
   user = db.query(model.Users).filter(model.Users.email==email).first()
   if not user:
      raise HTTPException(status_code=404, detail="User Not Found")
   
   user.username = updateUser.username
   user.full_name = updateUser.full_name
   user.email = updateUser.email

   db.commit()
   db.refresh(user)

   return user

# Course Crud 
# =============================================================
# Create Course 
def create_new_course(db: Session, course: schemas.RegisterCourse, lecturer_id: int):
    db_course = model.Course(
        course_name=course.course_name,
        course_code=course.course_code,
        description=course.description,
        lecturer_id=lecturer_id
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

# Get All Courses
def get_all_courses(db: Session):
    return db.query(model.Course).all()
# Get Course by ID
def get_course_by_id(db: Session, course_id: int):
    return db.query(model.Course).filter(model.Course.course_id == course_id).first()


