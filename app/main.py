from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import Base, SessionLocal, engine
import schemas, crud
from dependencies import get_db
from auth import pwd_context, oauth2_scheme, authenticate_user, create_access_token, get_current_user 


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "Welcome To The Assignment Submission System"}

# User management endpoints
#register a new user
@app.post("/users/signup/", response_model=schemas.UserResponse)
async def signUp(user: schemas.UserCreate, db: Session = Depends(get_db)):
    check_email = crud.check_email(db, email = user.email)
    if check_email:
        raise HTTPException(status_code=400, detail="Email Has been used")
    check_username = crud.check_username(db, username=user.username)
    if check_username:
        raise HTTPException(status_code=400, detail="Username Taken")
    hashed_password = pwd_context.hash(user.password)
    new_user = crud.Sign_up(db=db, user=user, hashed_password = hashed_password)
    return new_user
              
# User Login
@app.post("/users/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
