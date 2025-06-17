from typing import List
from fastapi import APIRouter, Depends

from auth import get_current_user, get_db
from constants import TIME_FORMAT
import json_classes
from logic.assignments import (
    create_assignment as logic_create_assignment,
    remove_assignment as logic_remove_assignment,
    get_assignment as logic_get_assignment,
    submit_assignment as logic_submit_assignment,
    get_assignment_submissions as logic_get_assignment_submissions,
    get_submission as logic_get_submission,
    grade_submission as logic_grade_submission,
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
        return logic_create_assignment(
            db_conn, db_cursor, course_id, title, description, user_email
        )


@router.post("/remove_assignment", response_model=json_classes.Success)
async def remove_assignment(
    course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)
):
    """
    Remove the assignment by the provided course_id and assignment_id.

    Teacher role required.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):
        return logic_remove_assignment(
            db_conn, db_cursor, course_id, assignment_id, user_email
        )


@router.get("/get_assignment", response_model=json_classes.Assignment)
async def get_assignment(
    course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)
):
    f"""
    Get the assignment details by the provided (course_id, assignment_id).

    Returns course_id, assignment_id, creation_time, title, description, and email of the author.

    Author can be 'null' if the author deleted their account.

    The format of creation time is "{TIME_FORMAT}".
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):
        return logic_get_assignment(db_cursor, course_id, assignment_id, user_email)


@router.post("/submit_assignment", response_model=json_classes.Success)
async def submit_assignment(
    course_id: str,
    assignment_id: str,
    comment: str,
    student_email: str = Depends(get_current_user),
):
    """
    Allows student to submit their assignment.

    Student role required.

    Student cannot submit already graded assignment.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):
        return logic_submit_assignment(
            db_conn, db_cursor, course_id, assignment_id, comment, student_email
        )


@router.get("/get_assignment_submissions", response_model=List[json_classes.Submission])
async def get_assignment_submissions(
    course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)
):
    f"""
    Get the list of students submissions of provided assignments.

    Teacher role required.

    Submissions are ordered by submission_time, the first submissions are new.

    Returns the list of submissions (course_id, assignment_id, student_email, student_name, submission_time, last_modification_time, comment, grade, gradedby_email).

    The format of submission_time and last_modification_time is "{TIME_FORMAT}".

    `grade` and `gradedby_email` can be `null` if the assignment was not graded yet.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):
        return logic_get_assignment_submissions(
            db_cursor, course_id, assignment_id, user_email
        )


@router.get("/get_submission", response_model=json_classes.Submission)
async def get_submission(
    course_id: str,
    assignment_id: str,
    student_email: str,
    user_email: str = Depends(get_current_user),
):
    f"""
    Get the student submission of assignment by course_id, assignment_id and student_email.

    - Teacher can get all submissions of the course
    - Parent can get the submission of their student
    - Stuent can get their submissions

    Returns the submission (course_id, assignment_id, student_email, student_name, submission_time, last_modification_time, comment, grade, gradedby_email).

    The format of submission_time and last_modification_time is "{TIME_FORMAT}".

    `grade` and `gradedby_email` can be `null` if the assignment was not graded yet.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):
        return logic_get_submission(
            db_cursor, course_id, assignment_id, student_email, user_email
        )


@router.post("/grade_submission", response_model=json_classes.Success)
async def grade_submission(
    course_id: str,
    assignment_id: str,
    student_email: str,
    grade: str,
    user_email: str = Depends(get_current_user),
):
    """
    Allows teacher to grade student's submission.

    Teacher role required.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):
        return logic_grade_submission(
            db_conn,
            db_cursor,
            course_id,
            assignment_id,
            student_email,
            grade,
            user_email,
        )
