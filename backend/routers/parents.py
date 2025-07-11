from typing import List
from fastapi import APIRouter, Depends

from auth import get_current_user
from logic.parents import (
    get_students_parents as logic_get_students_parents,
    invite_parent as logic_invite_parent,
    remove_parent as logic_remove_parent,
    get_parents_children as logic_get_parents_children,
)
import json_classes
import constraints

import database

router = APIRouter()


@router.get("/get_students_parents", response_model=List[json_classes.User])
async def get_students_parents(course_id: str, student_email: str, user_email: str = Depends(get_current_user)):
    """
    Get the list of parents observing the student with provided email on course with provided course_id.

    Teacher role required.
    """
    with database.get_system_conn() as db_conn:
        constraints.assert_student_access(db_conn, student_email, course_id)
        constraints.assert_teacher_access(db_conn, user_email, course_id)
        parents = logic_get_students_parents(db_conn, course_id, student_email, user_email)
        return [{"email": par.email, "name": par.publicname} for par in parents]


@router.post("/invite_parent", response_model=json_classes.Success)
async def invite_parent(
    course_id: str,
    student_email: str,
    parent_email: str,
    teacher_email: str = Depends(get_current_user),
):
    """
    Invite the user with provided parent_email to become a parent of the student with provided student_email on course with provided course_id.

    Teacher role required.
    """
    with database.get_system_conn() as db_conn:
        constraints.assert_teacher_access(db_conn, teacher_email, course_id)
        constraints.assert_student_access(db_conn, student_email, course_id)
        return logic_invite_parent(db_conn, course_id, student_email, parent_email, teacher_email)


@router.post("/remove_parent", response_model=json_classes.Success)
async def remove_parent(
    course_id: str,
    student_email: str,
    parent_email: str,
    user_email: str = Depends(get_current_user),
):
    """
    Remove the parent identified by parent_email from the tracking of student with provided student_email on course with provided course_id.

    Teacher OR Parent role required.

    Parent can only remove themselves.
    """

    with database.get_system_conn() as db_conn:
        return logic_remove_parent(db_conn, course_id, student_email, parent_email, user_email)


@router.get("/get_parents_children", response_model=List[json_classes.User])
async def get_parents_children(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the list of students for the parent with provided email on course with provided course_id.

    Parent role required.
    """

    with database.get_system_conn() as db_conn:
        return logic_get_parents_children(db_conn, course_id, user_email)
