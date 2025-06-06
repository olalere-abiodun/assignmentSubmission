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

# Check for Email
def check_email(db: Session, email:str):
   return db.query(model.Users).filter(model.Users.email == email).first()

def check_username(db: Session, username:str):
   return db.query(model.Users).filter(model.Users.username == username).first()
# Check for Username Exist


