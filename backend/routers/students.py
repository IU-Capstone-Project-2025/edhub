from typing import List
from fastapi import APIRouter, Depends

from auth import get_current_user
import database
import json_classes
from logic.students import (
    get_enrolled_students as logic_get_enrolled_students,
    invite_student as logic_invite_student,
    remove_student as logic_remove_student,
)
import logic.logging as logger
import constraints
import edhub_errors

router = APIRouter()


@router.get("/get_enrolled_students", response_model=List[json_classes.User])
async def get_enrolled_students(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the list of enrolled students by course_id.

    Return the email and name of each student.
    """
    with database.get_system_conn() as conn:
        constraints.assert_course_access(conn, user_email, course_id)
        students = logic_get_enrolled_students(conn, course_id)
        return [json_classes.User.from_dto(s) for s in students]


@router.post("/invite_student", response_model=json_classes.Success)
async def invite_student(course_id: str, student_email: str, teacher_email: str = Depends(get_current_user)):
    """
    Add the student with provided email to the course with provided course_id.

    Teacher role required.
    """
    with database.get_system_conn() as conn:
        constraints.assert_teacher_or_admin_access(conn, teacher_email, course_id)
        logic_invite_student(conn, course_id, student_email, teacher_email)
        logger.log(conn, logger.TAG_STUDENT_ADD, f"Teacher {teacher_email} invited a student {student_email}")
    return json_classes.successful


@router.post("/remove_student", response_model=json_classes.Success)
async def remove_student(course_id: str, student_email: str, user_email: str = Depends(get_current_user)):
    """
    Remove the student with provided email from the course with provided course_id.

    Teacher OR Student role required.

    Student can only remove themselves.
    """
    with database.get_system_conn() as conn:
        if not (
            constraints.check_teacher_or_admin_access(conn, user_email, course_id)
            or (constraints.check_student_access(conn, user_email, course_id) and student_email == user_email)
        ):
            raise edhub_errors.CannotRemoveStudentException(course_id, user_email, student_email)
        logic_remove_student(conn, course_id, student_email, user_email)
        logger.log(conn, logger.TAG_STUDENT_DEL, f"Teacher {user_email} removed a student {student_email}")
    return json_classes.successful
