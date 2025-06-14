from typing import List
from routers.auth import get_current_user, get_db
from fastapi import APIRouter, Depends
import models.api
import logic.user as user_logic
import repository.users as repo_users
import repository.courses as courses_repo

router = APIRouter()


@router.get("/get_enrolled_students", response_model=List[models.api.User])
async def get_enrolled_students(
    course_id: str, user_email: str = Depends(get_current_user)
):
    """
    Get the list of enrolled students by course_id.

    Return the email and name of the student.
    """

    with get_db() as (db_conn, db_cursor):

        courses_repo.assert_course_exists(db_cursor, course_id)
        courses_repo.assert_course_access(db_cursor, user_email, course_id)

        res = repo_users.get_enrolled_students(db_conn, course_id)
        return res


@router.post("/invite_student", response_model=models.api.Success)
async def invite_student(
    course_id: str, student_email: str, teacher_email: str = Depends(get_current_user)
):
    """
    Add the student with provided email to the course with provided course_id.

    Teacher role required.
    """

    with get_db() as (db_conn, db_cursor):

        return user_logic.invite_student_logic(
            db_cursor, db_conn, course_id, student_email, teacher_email
        )


@router.post("/remove_student", response_model=models.api.Success)
async def remove_student(
    course_id: str, student_email: str, teacher_email: str = Depends(get_current_user)
):
    """
    Remove the student with provided email from the course with provided course_id.

    Teacher role required.
    """

    with get_db() as (db_conn, db_cursor):

        return user_logic.remove_student_logic(
            db_cursor, db_conn, course_id, student_email, teacher_email
        )


@router.get("/get_students_parents", response_model=List[models.api.User])
async def get_students_parents(
    course_id: str, student_email: str, user_email: str = Depends(get_current_user)
):
    """
    Get the list of parents observing the student with provided email on course with provided course_id.

    Teacher role required.
    """

    with get_db() as (db_conn, db_cursor):

        return user_logic.get_students_parents_logic(
            db_cursor, course_id, student_email, user_email
        )


@router.post("/invite_parent", response_model=models.api.Success)
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

    with get_db() as (db_conn, db_cursor):

        return user_logic.invite_parent_logic(
            db_cursor, db_conn, course_id, student_email, parent_email, teacher_email
        )


@router.post("/remove_parent", response_model=models.api.Success)
async def remove_parent(
    course_id: str,
    student_email: str,
    parent_email: str,
    teacher_email: str = Depends(get_current_user),
):
    """
    Remove the parent identified by parent_email from the tracking of student with provided student_email on course with provided course_id.

    Teacher role required.
    """

    with get_db() as (db_conn, db_cursor):

        return user_logic.remove_parent_logic(
            db_cursor, db_conn, course_id, student_email, parent_email, teacher_email
        )


@router.get("/get_course_teachers", response_model=List[models.api.User])
async def get_course_teachers(
    course_id: str, user_email: str = Depends(get_current_user)
):
    """
    Get the list of teachers teaching the course with the provided course_id.
    """

    with get_db() as (db_conn, db_cursor):

        return user_logic.get_course_teachers_logic(db_cursor, course_id, user_email)


@router.post("/invite_teacher", response_model=models.api.Success)
async def invite_teacher(
    course_id: str,
    new_teacher_email: str,
    teacher_email: str = Depends(get_current_user),
):
    """
    Add the user with provided new_teacher_email as a techer to the course with provided course_id.

    Teacher role required.
    """

    with get_db() as (db_conn, db_cursor):

        return user_logic.invite_teacher_logic(
            db_cursor, db_conn, course_id, new_teacher_email, teacher_email
        )


@router.post("/remove_teacher", response_model=models.api.Success)
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

        return user_logic.remove_teacher_logic(
            db_cursor, db_conn, course_id, removing_teacher_email, teacher_email
        )
