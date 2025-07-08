from fastapi import HTTPException
from datetime import datetime, timedelta
from jose import jwt
import constraints
from auth import pwd_hasher, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
import repo.users as repo_users
from regex import match, search
import logic.logging as logger
from secrets import token_hex


def get_user_info(db_cursor, user_email: str):
    return {
        "email": user_email,
        "name": repo_users.sql_get_user_name(db_cursor, user_email),
    }


def get_user_role(db_cursor, course_id: str, user_email: str):
    # getting info about the roles
    res = {
        "is_teacher": constraints.check_teacher_access(db_cursor, user_email, course_id),
        "is_student": constraints.check_student_access(db_cursor, user_email, course_id),
        "is_parent": constraints.check_parent_access(db_cursor, user_email, course_id),
        "is_admin": constraints.check_admin_access(db_cursor, user_email)
    }

    return res


def create_user(db_conn, db_cursor, user):

    # validation of email format
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not (
        match(pattern, user.email)
        and len(user.email) <= 254
        and not ".." in user.email
        and len(user.email.split("@")[0]) <= 64
    ):
        raise HTTPException(status_code=400, detail="Incorrect email format")

    # validation of password complexity (length, digit(s), letter(s), special symbol(s))
    if not (
        len(user.password) >= 8
        and search(r"\d", user.password)
        and search(r"\p{L}", user.password)
        and search(r"[^\p{L}\p{N}\s]", user.password)
    ):
        raise HTTPException(status_code=400, detail="Password is too weak")

    # checking whether such user exists
    user_exists = repo_users.sql_select_user_exists(db_cursor, user.email)
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")

    # hashing password
    hashed_password = pwd_hasher.hash(user.password)
    repo_users.sql_insert_user(db_cursor, user.email, user.name, hashed_password)
    db_conn.commit()

    # giving access_token
    data = {
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    logger.log(db_conn, logger.TAG_USER_ADD, f"Created new user: {user.email}")

    return {"email": user.email, "access_token": access_token}


def login(db_cursor, user):

    result = repo_users.sql_select_passwordhash(db_cursor, user.email)

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


def change_password(db_conn, db_cursor, user):

    result = repo_users.sql_select_passwordhash(db_cursor, user.email)

    # checking whether such user exists
    if not result:
        raise HTTPException(status_code=401, detail="Invalid user email")

    # checking password
    hashed_password = result[0]
    if not pwd_hasher.verify(user.password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    # changing the password to a new one
    hashed_new_password = pwd_hasher.hash(user.new_password)
    repo_users.sql_update_password(db_cursor, user.email, hashed_new_password)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_USER_CHPW, f"User {user.email} changed their password")

    return {"success": True}


def remove_user(db_conn, db_cursor, user_email: str):

    # checking constraints
    constraints.assert_user_exists(db_cursor, user_email)
    if repo_users.sql_count_admins(db_cursor) == 1:
        raise HTTPException(status_code=403, detail="Cannot remove the last administrator")

    # remove teacher role preparation: find courses with 1 teacher left
    single_teacher_courses = repo_users.sql_select_single_teacher_courses(db_cursor, user_email)
    for course_id_to_delete in single_teacher_courses:  # Renamed variable to avoid conflict
        repo_users.sql_delete_course(db_cursor, course_id_to_delete)

    # remove user
    repo_users.sql_delete_user(db_cursor, user_email)

    db_conn.commit()

    logger.log(db_conn, logger.TAG_USER_DEL, f"Removed user {user_email} from the system")

    return {"success": True}


def check_admin_exists(db_cursor) -> bool:
    return constraints.check_user_exists(db_cursor, "admin")


def create_admin_account(db_conn, db_cursor):
    password = token_hex(32)
    hashed_password = pwd_hasher.hash(password)
    repo_users.sql_insert_user(db_cursor, 'admin', 'admin', hashed_password)
    repo_users.sql_give_admin_permissions(db_cursor, 'admin')
    db_conn.commit()

    logger.log(db_conn, logger.TAG_USER_ADD, f"Created new user: admin")
    logger.log(db_conn, logger.TAG_ADMIN_ADD, f"Added admin privileges to user: admin")

    return password


def give_admin_permissions(db_conn, db_cursor, object_email: str, subject_email: str):

    # checking constraints
    constraints.assert_admin_access(db_cursor, subject_email)
    constraints.assert_user_exists(db_cursor, object_email)

    repo_users.sql_give_admin_permissions(db_cursor, object_email)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_ADMIN_ADD, f"Added admin privileges to user: admin")

    return {"success": True}


def get_all_users(db_cursor, user_email: str):
    # checking constraints
    constraints.assert_admin_access(db_cursor, user_email)

    # finding all users
    users = repo_users.sql_select_all_users(db_cursor)

    res = [{"email": u[0], "name": u[1]} for u in users]
    return res
