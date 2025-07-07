from fastapi import APIRouter, Depends

from auth import get_current_user, get_db
import json_classes
from logic.users import (
    get_user_info as logic_get_user_info,
    get_user_role as logic_get_user_role,
    create_user as logic_create_user,
    login as logic_login,
    change_password as logic_change_password,
    remove_user as logic_remove_user,
    give_admin_permissions as logic_give_admin_permissions
)

router = APIRouter()


@router.get("/get_user_info", response_model=json_classes.User)
async def get_user_info(user_email: str = Depends(get_current_user)):
    """
    Get the info about the user.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_get_user_info(db_cursor, user_email)


@router.get("/get_user_role", response_model=json_classes.CourseRole)
async def get_user_role(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the user's role in the provided course.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_get_user_role(db_cursor, course_id, user_email)


@router.post("/create_user", response_model=json_classes.Account)
async def create_user(user: json_classes.UserCreate):
    """
    Creates a user account with provided email, name, and password.

    User email should be in the correct format.

    User password should have at least 8 symbols and contain digits, letters, and special symbols.

    Returns email and JWT access token for 30 minutes.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_create_user(db_conn, db_cursor, user)


@router.post("/login", response_model=json_classes.Account)
async def login(user: json_classes.UserLogin):
    """
    Log into user account with provided email and password.

    Returns email and JWT access token for 30 minutes.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_login(db_cursor, user)


@router.post("/change_password", response_model=json_classes.Success)
async def change_password(user: json_classes.UserNewPassword):
    """
    Change the user password to a new one.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_change_password(db_conn, db_cursor, user)


@router.post("/remove_user", response_model=json_classes.Success)
async def remove_user(user_email: str = Depends(get_current_user)):
    """
    Delete user account from the system.

    The user will be removed from courses where they were a Parent.

    The user will be removed from courses where they were a Student.

    The user's assignment submissions will be removed.

    Courses where the user is the only Teacher will be deleted.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_remove_user(db_conn, db_cursor, user_email)


@router.post("/give_admin_permissions", response_model=json_classes.Success)
async def give_admin_permissions(object_email: str, subject_email: str = Depends(get_current_user)):
    """
    Give admin rights to some existing uesr.

    Admin role required.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_give_admin_permissions(db_conn, db_cursor, object_email, subject_email)
