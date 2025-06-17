from typing import List
from fastapi import APIRouter, Depends

from auth import get_current_user, get_db
from constants import TIME_FORMAT
import json_classes
from logic.users import (
    get_user_role as logic_get_user_role,
    create_user as logic_create_user,
    login as logic_login,
    remove_user as logic_remove_user,
)

router = APIRouter()


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

    Returns email and JWT access token for 30 minutes.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_create_user(
            db_conn,
            db_cursor,
            user
        )


@router.post("/login", response_model=json_classes.Account)
async def login(user: json_classes.UserLogin):
    """
    Log into user account with provided email and password.

    Returns email and JWT access token for 30 minutes.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_login(
            db_cursor,
            user
        )


# WARNING: update if new elements appear
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
