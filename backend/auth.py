from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from contextlib import contextmanager
from secrets import token_hex
from jose import jwt
import psycopg2
import json_classes
import constraints


@contextmanager
def get_db():
    conn = psycopg2.connect(dbname="edhub", user="postgres", password="12345678", host="db", port="5432")
    cursor = conn.cursor()
    try:
        yield conn, cursor
    finally:
        cursor.close()
        conn.close()


router = APIRouter()

# setting for JWT and autorization
# TODO: insert secret key from .env (in production)
SECRET_KEY = token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("email")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    # checking whether such user exists
    with get_db() as (db_conn, db_cursor):
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (user_email,))
        user_exists = db_cursor.fetchone()[0]
        if not user_exists:
            raise HTTPException(status_code=401, detail="User not exists")

    return user_email


@router.post('/create_user', response_model=json_classes.Account)
async def create_user(user: json_classes.UserCreate):
    '''
    Creates a user account with provided email, name, and password.

    Returns email and JWT access token for 30 minutes.
    '''

    with get_db() as (db_conn, db_cursor):

        # checking whether such user exists
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (user.email,))
        user_exists = db_cursor.fetchone()[0]
        if user_exists:
            raise HTTPException(status_code=400, detail="User already exists")

        # hashing password
        hashed_password = pwd_hasher.hash(user.password)
        db_cursor.execute(
            "INSERT INTO users (email, publicname, isadmin, timeregistered, passwordhash) VALUES (%s, %s, %s, now(), %s)",
            (user.email, user.name, False, hashed_password)
        )
        db_conn.commit()

    # giving access_token
    data = {"email": user.email, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return {"email": user.email, "access_token": access_token}


@router.post('/login', response_model=json_classes.Account)
async def login(user: json_classes.UserLogin):
    '''
    Log into user account with provided email and password.

    Returns email and JWT access token for 30 minutes.
    '''

    with get_db() as (db_conn, db_cursor):
        db_cursor.execute("SELECT passwordhash FROM users WHERE email = %s", (user.email,))
        result = db_cursor.fetchone()

        # checking whether such user exists
        if not result:
            raise HTTPException(status_code=401, detail="Invalid user email")

        # checking password
        hashed_password = result[0]
        if not pwd_hasher.verify(user.password, hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")

    # giving access token
    data = {"email": user.email, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return {"email": user.email, "access_token": access_token}


# WARNING: update if new elements appear
@router.post('/remove_user', response_model=json_classes.Success)
async def remove_user(user_email: str = Depends(get_current_user)):
    '''
    Delete user account from the system.

    The user will be removed from courses where they were a Parent.

    The user will be removed from courses where they were a Student.

    The user's assignment submissions will be removed.

    Courses where the user is the only Teacher will be deleted.
    '''

    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_user_exists(db_cursor, user_email)

        # remove parent role
        db_cursor.execute("DELETE FROM parent_of_at_course WHERE parentemail = %s", (user_email,))

        # remove student role preparation: remove submissions
        db_cursor.execute("DELETE FROM course_assignments_submissions WHERE email = %s", (user_email,))

        # remove student role
        db_cursor.execute("DELETE FROM student_at WHERE email = %s", (user_email,))

        # remove teacher role preparation: find courses with 1 teacher left
        db_cursor.execute('''
            SELECT t.courseid 
            FROM teaches t
            WHERE t.email = %s
            AND (SELECT COUNT(*) FROM teaches WHERE courseid = t.courseid) = 1
        ''', (user_email,))
        single_teacher_courses = [row[0] for row in db_cursor.fetchall()]

        # remove teacher role preparation: remove courses with 1 teacher left
        for course_id in single_teacher_courses:
            db_cursor.execute("DELETE FROM course_assignments_submissions WHERE courseid = %s", (course_id,))
            db_cursor.execute("DELETE FROM course_materials WHERE courseid = %s", (course_id,))
            db_cursor.execute("DELETE FROM course_assignments WHERE courseid = %s", (course_id,))
            db_cursor.execute("DELETE FROM student_at WHERE courseid = %s", (course_id,))
            db_cursor.execute("DELETE FROM parent_of_at_course WHERE courseid = %s", (course_id,))
            db_cursor.execute("DELETE FROM teaches WHERE courseid = %s", (course_id,))
            db_cursor.execute("DELETE FROM courses WHERE courseid = %s", (course_id,))

        # remove teacher role preparation: update published posts
        db_cursor.execute("UPDATE course_materials SET author = NULL WHERE author = %s", (user_email,))
        db_cursor.execute("UPDATE course_assignments SET author = NULL WHERE author = %s", (user_email,))

        # remove teacher role
        db_cursor.execute("DELETE FROM teaches WHERE email = %s", (user_email,))

        # remove user
        db_cursor.execute("DELETE FROM users WHERE email = %s", (user_email,))

        db_conn.commit()

    return {"success": True}
