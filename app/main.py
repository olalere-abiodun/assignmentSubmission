from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import Base, SessionLocal, engine
import schemas, crud, model
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

#Edit User
@app.put("/users/me", response_model=schemas.UserResponse)
async def update_user_profile(updateUser: schemas.UserUpdate,db: Session = Depends(get_db),current_user: schemas.User = Depends(get_current_user)):
    user = crud.check_username(db, username=current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")

    updated_user = crud.UpdateUser(db=db, email=current_user.email, updateUser=updateUser)
    return updated_user

# Course Management endpoints
# Create a new course
@app.post("/courses/", response_model=schemas.CourseResponse)
async def create_course(course: schemas.RegisterCourse, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "lecturer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can create courses")
    # Get the lecturer ID from the current user
    lecturer_id = current_user.user_id
    new_course = crud.create_new_course(db=db, course=course, lecturer_id=lecturer_id)
    return new_course

# Get all courses
@app.get("/courses/", response_model=list[schemas.CourseResponse])
async def get_all_courses(db: Session = Depends(get_db)):
    courses = crud.get_all_courses(db=db)
    return courses

# Get course by ID
@app.get("/courses/{course_id}", response_model=schemas.CourseResponse)
async def get_course_by_id(course_id: int, db: Session = Depends(get_db)):
    course = crud.get_course_by_id(db=db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

# Get course by course code
@app.get("/courses/code/{course_code}", response_model=schemas.CourseResponse)
async def get_course_by_code(course_code: str, db: Session = Depends(get_db)):
    course = crud.get_course_by_code(db=db, course_code=course_code)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

# Update course by ID
@app.put("/courses/{course_id}", response_model=schemas.CourseResponse)
async def update_course(course_id: int, course_update: schemas.CourseUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "lecturer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can update courses")
    # Check if the user is the lecturer of the course
    course = crud.get_course_by_id(db=db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found") 
    if course.lecturer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this course")
    # Update the course
    updated_course = crud.update_course(db=db, course_id=course_id, course_update=course_update)
    return updated_course

# Update course by course code
@app.put("/courses/code/{course_code}", response_model=schemas.CourseResponse)
async def update_course_by_code(course_code: str, course_update: schemas.CourseUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "lecturer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can update courses")
    # Check if the user is the lecturer of the course
    course = crud.get_course_by_code(db=db, course_code=course_code)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.lecturer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this course")
    # Update the course
    updated_course = crud.update_course_by_code(db=db, course_code=course_code, course_update=course_update)
    return updated_course


# Enroll in a course
@app.post("/courses/{course_id}/enroll", response_model=schemas.EnrollResponse)
async def enroll_in_course(course_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    user_id = current_user.user_id
    # Get Course name by course_id
    course = crud.get_course_by_id(db=db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    # Check if the user is already enrolled in the course
    existing_enrollment = db.query(model.Enrollment).filter(
        model.Enrollment.user_id == user_id,
        model.Enrollment.course_id == course_id
    ).first()
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
    # Create a new enrollment
    enrollment = crud.new_enroll(db=db, user_id=user_id, course_id=course_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Course not found or already enrolled")
    return schemas.EnrollResponse(
        username=current_user.username,          
        course_name=course.course_name,
        course_code=course.course_code,
        lecturer_id=course.lecturer_id
    )
# Get all enrollments for a user
@app.get("/users/me/enrollments", response_model=list[schemas.EnrollResponse])
async def get_user_enrollments(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    user_id = current_user.user_id
    enrollments = crud.get_enrollments_by_user_id(db=db, user_id=current_user.user_id)
    if not enrollments:
        raise HTTPException(status_code=404, detail="No enrollments found")
    
    response = []
    for enrollment in enrollments:
        course = crud.get_course_by_id(db=db, course_id=enrollment.course_id)
        if course:
            response.append(schemas.EnrollResponse(
                username=current_user.username,
                course_name=course.course_name,
                course_code=course.course_code,
                lecturer_id=course.lecturer_id
            ))
    return response

# Unenroll from a course
@app.delete("/courses/{course_id}/unenroll", response_model=schemas.EnrollResponse)
async def unenroll_from_course(course_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    user_id = current_user.user_id
    # Check if the user is enrolled in the course
    enrollment = db.query(model.Enrollment).filter(
        model.Enrollment.user_id == user_id,
        model.Enrollment.course_id == course_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Unenroll the user from the course
    db.delete(enrollment)
    db.commit()
    
    # Get Course name by course_id
    course = crud.get_course_by_id(db=db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return schemas.EnrollResponse(
        username=current_user.username,
        course_name=course.course_name,
        course_code=course.course_code,
        lecturer_id=course.lecturer_id
    )

# Assignment Management endpoints
# Create a new assignment
@app.post("/assignments/", response_model=schemas.AssignmentResponse)
async def create_assignment(assignment: schemas.AssignmentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "lecturer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can create assignments")

    # Create the assignment
    new_assignment = crud.create_assignment(db=db, assignment=assignment, lecturer_id=current_user.user_id)
    return new_assignment

# Get assignemt by ID
@app.get("/assignments/{assignment_id}", response_model=schemas.AssignmentResponse)
async def get_assignment_by_id(assignment_id: int, db: Session = Depends(get_db)):
    assignment = crud.get_assignment_by_id(db=db, assignment_id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return 
