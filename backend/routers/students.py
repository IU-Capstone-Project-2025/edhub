from typing import List
from fastapi import APIRouter, Depends

from auth import get_current_user, get_db
import json_classes
from logic.students import (
    get_enrolled_students as logic_get_enrolled_students,
    invite_student as logic_invite_student,
    remove_student as logic_remove_student,
)

router = APIRouter()


@router.get("/get_enrolled_students", response_model=List[json_classes.User])
async def get_enrolled_students(
    course_id: str, user_email: str = Depends(get_current_user)
):
    """
    Get the list of enrolled students by course_id.

    Return the email and name of the student.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_get_enrolled_students(db_cursor, course_id, user_email)


@router.post("/invite_student", response_model=json_classes.Success)
async def invite_student(
    course_id: str, student_email: str, teacher_email: str = Depends(get_current_user)
):
    """
    Add the student with provided email to the course with provided course_id.

    Teacher role required.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_invite_student(
            db_conn, db_cursor, course_id, student_email, teacher_email
        )


@router.post("/remove_student", response_model=json_classes.Success)
async def remove_student(
    course_id: str, student_email: str, teacher_email: str = Depends(get_current_user)
):
    """
    Remove the student with provided email from the course with provided course_id.

    Teacher role required.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_remove_student(
            db_conn, db_cursor, course_id, student_email, teacher_email
        )
    with get_db() as (db_conn, db_cursor):
        return ...
