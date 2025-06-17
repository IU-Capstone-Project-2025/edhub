from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from secrets import token_hex
from jose import jwt
import constraints
from auth import pwd_hasher, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


def get_user_role(db_cursor, course_id: str, user_email: str):
    # getting info about the roles
    res = {
        "is_teacher": constraints.check_teacher_access(
            db_cursor, user_email, course_id
        ),
        "is_student": constraints.check_student_access(
            db_cursor, user_email, course_id
        ),
        "is_parent": constraints.check_parent_access(db_cursor, user_email, course_id),
    }

    return res


def create_user(db_conn, db_cursor, user):

    # checking whether such user exists
    db_cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (user.email,)
    )
    user_exists = db_cursor.fetchone()[0]
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")

    # hashing password
    hashed_password = pwd_hasher.hash(user.password)
    db_cursor.execute(
        "INSERT INTO users (email, publicname, isadmin, timeregistered, passwordhash) VALUES (%s, %s, %s, now(), %s)",
        (user.email, user.name, False, hashed_password),
    )
    db_conn.commit()

    # giving access_token
    data = {
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return {"email": user.email, "access_token": access_token}


def login(db_cursor, user):

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
    data = {
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return {"email": user.email, "access_token": access_token}


def remove_user(db_conn, db_cursor, user_email: str):

    # checking constraints
    constraints.assert_user_exists(db_cursor, user_email)

    # remove teacher role preparation: find courses with 1 teacher left
    db_cursor.execute(
        "SELECT t.courseid FROM teaches t WHERE t.email = %s AND (SELECT COUNT(*) FROM teaches WHERE courseid = t.courseid) = 1",
        (user_email,),
    )
    single_teacher_courses = [row[0] for row in db_cursor.fetchall()]

    # remove teacher role preparation: remove courses with 1 teacher left
    for (
        course_id_to_delete
    ) in single_teacher_courses:  # Renamed variable to avoid conflict
        db_cursor.execute(
            "DELETE FROM courses WHERE courseid = %s", (course_id_to_delete,)
        )

    # remove user
    db_cursor.execute("DELETE FROM users WHERE email = %s", (user_email,))

    db_conn.commit()

    return {"success": True}
