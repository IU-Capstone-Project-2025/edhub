import edhub_errors
from datetime import datetime, timedelta
from jose import jwt
import constraints
from auth import pwd_hasher, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
import sql.users as sql_users
from regex import match, search
from secrets import token_hex
from sql.dto import UserEmailNameDTO, UserRolesDTO
from json_classes import UserCreate
from logic.logging import logger


def get_user_info(conn, user_email: str) -> UserEmailNameDTO:
    return UserEmailNameDTO(user_email, sql_users.get_user_name(conn, user_email))


def get_user_role(conn, course_id: str, user_email: str) -> UserRolesDTO:
    return UserRolesDTO(
        is_teacher=constraints.check_teacher_access(conn, user_email, course_id),
        is_student=constraints.check_student_access(conn, user_email, course_id),
        is_parent=constraints.check_parent_access(conn, user_email, course_id),
        is_admin=constraints.check_admin_access(conn, user_email),
    )


def create_user(conn, email: str, password: str, publicname: str) -> None:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not (
        match(pattern, user.email)
        and len(user.email) <= 254
        and not ".." in user.email
        and len(user.email.split("@")[0]) <= 64
    ):
        raise edhub_errors.BadEmailFormatException(user.email)

    if not (
        len(user.password) >= 8
        and search(r"\d", user.password)
        and search(r"\p{L}", user.password)
        and search(r"[^\p{L}\p{N}\s]", user.password)
    ):
        raise edhub_errors.PasswordTooWeakException()

    constraints.assert_user_not_exists(conn, user.email)

    hashed_password = pwd_hasher.hash(user.password)
    sql_users.insert_user(conn, user.email, user.name, hashed_password)


def login(conn, email: str, password: str) -> str:
    """
    Asserts that the password is correct.

    If it is correct, returns a fresh access token.
    """
    constraints.assert_user_exists(conn, email)
    hashed_password = sql_users.select_passwordhash(conn, email)

    if not pwd_hasher.verify(password, hashed_password):
        raise edhub_errors.WrongPasswordException()
    return get_access_token(email)


def get_access_token(email: str) -> str:
    """
    Returns a token that represents logging in as `email`.
    Expires in `ACCESS_TOKEN_EXPIRE_MINUTES` from `datetime.utcnow()`.
    """
    data = {
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def change_password(conn, email: str, old_password: str, new_password: str) -> None:
    constraints.assert_user_exists(conn, email)
    hashed_password = sql_users.select_passwordhash(conn, email)
    if not pwd_hasher.verify(old_password, hashed_password):
        raise edhub_errors.WrongPasswordException()

    hashed_new_password = pwd_hasher.hash(new_password)
    sql_users.update_password(conn, email, hashed_new_password)


def remove_user(conn, user_email: str):
    constraints.assert_user_exists(conn, user_email)
    if sql_users.select_is_admin(conn, user_email) and sql_users.count_admins(conn) == 1:
        raise edhub_errors.CannotRemoveLastAdminException()

    # remove teacher role preparation: find courses
    single_teacher_courses = sql_users.select_single_teacher_courses(conn, user_email)
    for course_id_to_delete in single_teacher_courses:  # Renamed variable to avoid conflict
        sql_users.delete_course(conn, course_id_to_delete)

    sql_users.delete_user(conn, user_email)


def create_admin_account(conn) -> str:
    """
    Create a new user with login 'admin' and a random password. This function leaves a log message.

    Returns the random password.
    """
    password = token_hex(32)
    hashed_password = pwd_hasher.hash(password)
    sql_users.insert_user(conn, "admin", "admin", hashed_password)
    sql_users.give_admin_permissions(conn, "admin")
    logger.log(conn, logger.TAG_ADMIN_ADD, "Created an initial admin user 'admin'")
    return password


def give_admin_permissions(conn, target_email: str) -> None:
    constraints.assert_user_exists(conn, target_email)
    sql_users.give_admin_permissions(conn, target_email)


get_all_users = sql_users.select_all_users


def create_admin_account_if_not_exists(conn) -> None:
    if sql_users.admins_exist(conn):
        return
    password = create_admin_account(conn)
    credentials = f"login: admin\npassword: {password}"
    print(f"\nAdmin account created\n{credentials}\n")
    with open("random-secrets/admin_credentials.txt", "w") as f:
        print(credentials, file=f)
