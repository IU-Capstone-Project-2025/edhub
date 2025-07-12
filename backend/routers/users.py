from typing import List
from fastapi import APIRouter, Depends

from auth import get_current_user
import database
import json_classes
from logic.users import (
    get_user_info as logic_get_user_info,
    get_user_role as logic_get_user_role,
    create_user as logic_create_user,
    login as logic_login,
    change_password as logic_change_password,
    remove_user as logic_remove_user,
    give_admin_permissions as logic_give_admin_permissions,
    get_all_users as logic_get_all_users,
    get_access_token as logic_get_access_token,
)
import logic.logging as logger
import constraints

router = APIRouter()


@router.get("/get_user_info", response_model=json_classes.User)
async def get_user_info(user_email: str = Depends(get_current_user)):
    """
    Get the info about the user.
    """
    with database.get_system_conn() as conn:
        return json_classes.User.from_dto(logic_get_user_info(conn, user_email))


@router.get("/get_user_role", response_model=json_classes.CourseRole)
async def get_user_role(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the user's role in the provided course.
    """
    with database.get_system_conn() as conn:
        return json_classes.CourseRole.from_dto(logic_get_user_role(conn, course_id, user_email))


@router.post("/create_user", response_model=json_classes.Account)
async def create_user(user: json_classes.UserCreate):
    """
    Creates a user account with provided email, name, and password.

    User email should be in the correct format.

    User password should have at least 8 symbols and contain digits, letters, and special symbols.

    Returns email and JWT access token for 30 minutes.
    """
    with database.get_system_conn() as conn:
        logic_create_user(conn, user.email, user.password, user.name)
        logger.log(conn, logger.TAG_USER_ADD, f"Created new user: {user.email}")
    return {"email": user.email, "access_token": logic_get_access_token(user.email)}


@router.post("/login", response_model=json_classes.Account)
async def login(user: json_classes.UserLogin):
    """
    Log into user account with provided email and password.

    Returns email and JWT access token for 30 minutes.
    """
    with database.get_system_conn() as conn:
        return {"email": user.email, "access_token": logic_login(conn, user.email, user.password)}


@router.post("/change_password", response_model=json_classes.Success)
async def change_password(user: json_classes.UserNewPassword):
    """
    Change the user password to a new one.
    """
    with database.get_system_conn() as conn:
        logic_change_password(conn, user.email, user.password, user.new_password)
        logger.log(conn, logger.TAG_USER_CHPW, f"User {user.email} changed their password")
    return json_classes.Success()


@router.post("/remove_user", response_model=json_classes.Success)
async def remove_user(user_email: str = Depends(get_current_user)):
    """
    Delete user account from the system.

    The user will be removed from courses where they were a Parent.

    The user will be removed from courses where they were a Student.

    The user's assignment submissions will be removed.

    Courses where the user is the only Teacher will be deleted.
    """
    with database.get_system_conn() as conn:
        logic_remove_user(conn, user_email)
        logger.log(conn, logger.TAG_USER_DEL, f"Removed user {user_email} from the system")
    return json_classes.Success()


@router.post("/give_admin_permissions", response_model=json_classes.Success)
async def give_admin_permissions(object_email: str, my_email: str = Depends(get_current_user)):
    """
    Give admin rights to some existing user by their email.

    Admin role required.
    """
    with database.get_system_conn() as conn:
        constraints.assert_admin_access(conn, my_email)
        logic_give_admin_permissions(conn, object_email)
        logger.log(conn, logger.TAG_ADMIN_ADD, f"Added admin privileges to user: {object_email}")
    return json_classes.Success()


@router.get("/get_all_users", response_model=List[json_classes.User])
async def get_all_users(user_email: str = Depends(get_current_user)):
    """
    Get the list of all users in the system.

    Return the email and name of each user.

    Admin role required.
    """
    with database.get_system_conn() as conn:
        constraints.assert_admin_access(conn, user_email)
        return [{"email": user.email, "name": user.publicname} for user in logic_get_all_users(conn)]
