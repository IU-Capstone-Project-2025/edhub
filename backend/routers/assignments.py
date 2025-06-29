from fastapi import APIRouter, Depends

from auth import get_current_user, get_db
from constants import TIME_FORMAT
import json_classes
from logic.assignments import (
    create_assignment as logic_create_assignment,
    remove_assignment as logic_remove_assignment,
    get_assignment as logic_get_assignment
)


router = APIRouter()


@router.post("/create_assignment", response_model=json_classes.AssignmentID)
async def create_assignment(
    course_id: str,
    title: str,
    description: str,
    user_email: str = Depends(get_current_user),
):
    """
    Create the assignment with provided title and description in the course with provided course_id.

    Teacher role required.

    Returns the (course_id, assignment_id) for the new material in case of success.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):
        return logic_create_assignment(db_conn, db_cursor, course_id, title, description, user_email)


@router.post("/remove_assignment", response_model=json_classes.Success)
async def remove_assignment(course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)):
    """
    Remove the assignment by the provided course_id and assignment_id.

    Teacher role required.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):
        return logic_remove_assignment(db_conn, db_cursor, course_id, assignment_id, user_email)


@router.get("/get_assignment", response_model=json_classes.Assignment)
async def get_assignment(course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)):
    f"""
    Get the assignment details by the provided (course_id, assignment_id).

    Returns course_id, assignment_id, creation_time, title, description, and email of the author.

    Author can be 'null' if the author deleted their account.

    The format of creation time is "{TIME_FORMAT}".
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):
        return logic_get_assignment(db_cursor, course_id, assignment_id, user_email)
