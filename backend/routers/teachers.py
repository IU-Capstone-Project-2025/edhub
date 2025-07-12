from typing import List
from fastapi import APIRouter, Depends

from auth import get_current_user
import database
import json_classes
from logic.teachers import (
    get_course_teachers as logic_get_course_teachers,
    invite_teacher as logic_invite_teacher,
    remove_teacher as logic_remove_teacher,
)
import constraints
import logic.logging as logger

router = APIRouter()


@router.get("/get_course_teachers", response_model=List[json_classes.User])
async def get_course_teachers(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the list of teachers teaching the course with the provided course_id.
    """
    with database.get_system_conn() as conn:
        constraints.assert_course_access(conn, user_email, course_id)
        teachers = logic_get_course_teachers(conn, course_id, user_email)
    return [{"email": tch.email, "name": tch.publicname} for tch in teachers]


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
    with database.get_system_conn() as conn:
        constraints.assert_teacher_or_admin_access(conn, teacher_email, course_id)
        logic_invite_teacher(conn, course_id, new_teacher_email)
        logger.log(conn, logger.TAG_TEACHER_ADD, f"Teacher {teacher_email} invited a teacher {new_teacher_email}")
    return json_classes.Success()


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

    At least one teacher must stay in the course.
    """
    with database.get_system_conn() as conn:
        constraints.assert_teacher_or_admin_access(conn, teacher_email, course_id)
        logic_remove_teacher(conn, course_id, removing_teacher_email, teacher_email)
        logger.log(
            conn, logger.TAG_TEACHER_DEL, f"User {teacher_email} removed a teacher {removing_teacher_email}"
        )
    return json_classes.Success()
