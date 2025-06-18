from typing import List
from fastapi import APIRouter, Depends

from auth import get_current_user, get_db
import json_classes
from logic.teachers import (
    get_course_teachers as logic_get_course_teachers,
    invite_teacher as logic_invite_teacher,
    remove_teacher as logic_remove_teacher,
)

router = APIRouter()


@router.get("/get_course_teachers", response_model=List[json_classes.User])
async def get_course_teachers(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the list of teachers teaching the course with the provided course_id.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_get_course_teachers(db_cursor, course_id, user_email)


@router.post("/invite_teacher", response_model=json_classes.Success)
async def invite_teacher(
    course_id: str,
    new_teacher_email: str,
    teacher_email: str = Depends(get_current_user),
):
    """
    Add the user with provided new_teacher_email as a teacher to the course with provided course_id.

    Teacher role required.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_invite_teacher(db_conn, db_cursor, course_id, new_teacher_email, teacher_email)


@router.post("/remove_teacher", response_model=json_classes.Success)
async def remove_teacher(
    course_id: str,
    removing_teacher_email: str,
    teacher_email: str = Depends(get_current_user),
):
    """
    Remove the teacher with removing_teacher_email from the course with provided course_id.

    Teacher role required.

    Teacher can remove themself.

    At least one teacher should stay in the course.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_remove_teacher(db_conn, db_cursor, course_id, removing_teacher_email, teacher_email)
