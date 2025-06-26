from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File, Form
from pydantic import EmailStr
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
from datetime import datetime, date, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import Base, SessionLocal, engine
from app import schemas, crud, model
from app.dependencies import get_db
from app.auth import pwd_context, oauth2_scheme, authenticate_user, create_access_token, get_current_user 
import os
from my_logging.logger import get_logger

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploads"

app = FastAPI()

# Initialize logger
logger = get_logger(__name__)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount static files directory for serving uploaded files
app.mount("/static", StaticFiles(directory="uploads"), name="static")

@app.get("/")
async def home():
    logger.info("Home endpoint accessed")
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
    logger.info(f"New user created: {new_user.username}")
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
    logger.info(f"User logged in: {user.username}")
    # Return the access token and token type
    return {"access_token": access_token, "token_type": "bearer"}

#Edit User
@app.put("/users/me", response_model=schemas.UserResponse)
async def update_user_profile(updateUser: schemas.UserUpdate,db: Session = Depends(get_db),current_user: schemas.User = Depends(get_current_user)):
    user = crud.check_username(db, username=current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")

    updated_user = crud.UpdateUser(db=db, email=current_user.email, updateUser=updateUser)
    logger.info(f"User profile updated: {updated_user.username}")
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
    logger.info(f"New course created: {new_course.course_name} by lecturer ID: {lecturer_id}")
    return new_course

# Get all courses
@app.get("/courses/", response_model=list[schemas.CourseResponse])
async def get_all_courses(db: Session = Depends(get_db)):
    courses = crud.get_all_courses(db=db)
    logger.info(f"Retrieved {len(courses)} courses")
    return courses

# Get course by ID
@app.get("/courses/{course_id}", response_model=schemas.CourseResponse)
async def get_course_by_id(course_id: int, db: Session = Depends(get_db)):
    course = crud.get_course_by_id(db=db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    logger.info(f"Retrieved course: {course.course_name} with ID: {course_id}")
    return course

# Get course by course code
@app.get("/courses/code/{course_code}", response_model=schemas.CourseResponse)
async def get_course_by_code(course_code: str, db: Session = Depends(get_db)):
    course = crud.get_course_by_code(db=db, course_code=course_code)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    logger.info(f"Retrieved course: {course.course_name} with code: {course_code}")
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
    logger.info(f"Course updated: {updated_course.course_name} with ID: {course_id} by lecturer ID: {current_user.user_id}")
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
    logger.info(f"Course updated: {updated_course.course_name} with code: {course_code} by lecturer ID: {current_user.user_id}")
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
    logger.info(f"User {current_user.username} enrolled in course: {course.course_name} with ID: {course_id}")
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
    logger.info(f"Retrieved {len(response)} enrollments for user: {current_user.username}")
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
    logger.info(f"User {current_user.username} unenrolled from course: {course.course_name} with ID: {course_id}")
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
    logger.info(f"New assignment created: {new_assignment.assignment_title} for course ID: {assignment.course_id} by lecturer ID: {current_user.user_id}")
    return new_assignment

# Get assignemt by ID
@app.get("/assignments/{assignment_id}", response_model=schemas.AssignmentResponse)
async def get_assignment_by_id(assignment_id: int, db: Session = Depends(get_db)):
    assignment = crud.get_assignment_by_id(db=db, assignment_id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    logger.info(f"Retrieved assignment: {assignment.assignment_title} with ID: {assignment_id}")
    return assignment
# Edit assignment
@app.put("/assignments/{assignment_id}", response_model=schemas.AssignmentResponse)
async def update_assignment(assignment_id: int, assignment_update: schemas.AssignmentUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "lecturer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can update assignments")
    
    # Check if the assignment exists
    assignment = crud.get_assignment_by_id(db=db, assignment_id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Update the assignment
    updated_assignment = crud.update_assignment(db=db, assignment_id=assignment_id, assignment_update=assignment_update)
    logger.info(f"Assignment updated: {updated_assignment.assignment_title} with ID: {assignment_id} by lecturer ID: {current_user.user_id}")
    return updated_assignment

# Delete assignment 
@app.delete("/assignments/{assignment_id}", response_model=dict)
async def delete_assignment(assignment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "lecturer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can delete assignments")
    
    # Check if the assignment exists
    assignment = crud.get_assignment_by_id(db=db, assignment_id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Delete the assignment
    crud.delete_assignment(db=db, assignment_id=assignment_id)
    logger.info(f"Assignment deleted: {assignment.assignment_title} with ID: {assignment_id} by lecturer ID: {current_user.user_id}")
    return {"message": "Assignment deleted successfully"}

# Submission Management endpoints 
# Create a new submission
@app.post("/submissions/", response_model=schemas.SubmissionResponse)
async def submit_assignment(
    assignment_id: int = Form(...),
    content: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can submit assignments")
    
# Get the assignment
    assignment = crud.get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

# Check due date
    if datetime.utcnow() > assignment.due_date:
        raise HTTPException(status_code=403, detail="The submission deadline has passed.")


# Get the course_id associated with the assignment
    course_id = crud.get_course_id_by_assignment(db=db, assignment_id=assignment_id)
    if course_id is None:
        raise HTTPException(status_code=404, detail="Assignment not found")

# Now check if student is enrolled in the course
    if not crud.is_student_enrolled(db=db, student_id=current_user.user_id, course_id=course_id):
        raise HTTPException(status_code=403, detail="You are not enrolled in the course for this assignment")


    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # Save the uploaded file (optional — could be to disk or cloud like S3)
    file_url = None
    if file:
        filename = f"uploads/{file.filename}"
        with open(filename, "wb") as f:
            f.write(await file.read())
        file_url = f"/static/{file.filename}"  # or a full URL if hosted elsewhere

    # Create submission object
    submission_data = schemas.SubmissionCreate(
        assignment_id=assignment_id,
        student_id=current_user.user_id,
        content=content,
        file_url=file_url,
        submission_date=datetime.utcnow()
    )

    new_submission = crud.create_submission(db=db, submission=submission_data, student_id=current_user.user_id)
    logger.info(f"New submission created for assignment ID: {assignment_id} by student ID: {current_user.user_id}")
    return new_submission

# Output all submitted assignments for an assignment
@app.get("/submissions/{assignment_id}/all", response_model=list[schemas.AllSubmissionsResponse])
async def get_all_submissions(assignment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "lecturer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can view all submissions for an assignment")
    # Check if the assignment exists
    assignment = crud.get_assignment_by_id(db=db, assignment_id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    submissions = crud.get_all_assignment_submissions(db=db, assignment_id=assignment_id)
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found for this assignment")
    
    response = []
    for submission in submissions:
        response.append(schemas.AllSubmissionsResponse(
            submission_id=submission.submission_id,
            assignment_id=submission.assignment_id,
            user_id=submission.user_id,
            content=submission.content,
            file_url=submission.file_url,
            submission_date=submission.submission_date
        ))
    logger.info(f"Retrieved {len(response)} submissions for assignment ID: {assignment_id}")    
    return response

# Get all submissions by student
@app.get("/submissions/my", response_model=list[schemas.SubmissionResponse])
async def get_my_submissions(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can view their submissions")
    
    submissions = crud.get_submission_by_student(db=db, student_id=current_user.user_id)
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found for this student")
    
    response = []
    for submission in submissions:
        response.append(schemas.SubmissionResponse(
            submission_id=submission.submission_id,
            assignment_id=submission.assignment_id,
            user_id=submission.user_id,
            submission_date=submission.submission_date
        ))
    logger.info(f"Retrieved {len(response)} submissions for student ID: {current_user.user_id}")
    return response
# View my submission for a specific assignment 
@app.get("/submissions/{assignment_id}/me", response_model=schemas.SubmissionResponse)
async def get_my_submission_for_assignment(assignment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view their submission")
    submission = crud.get_submission_by_student_and_assignment(db, assignment_id=assignment_id, student_id=current_user.user_id)
    if not submission:
        raise HTTPException(status_code=404, detail="No submission found for this assignment")
    logger.info(f"Retrieved submission for assignment ID: {assignment_id} by student ID: {current_user.user_id}")
    return submission

@app.get("/download/{filename}")
async def download_file(filename: str):
    filepath = os.path.join("uploads", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    logger.info(f"File downloaded: {filename}")
    return FileResponse(path=filepath, filename=filename, media_type='application/octet-stream')






