from fastapi import APIRouter, Depends, UploadFile, File
from typing import List

from auth import get_current_user, get_db
from constants import TIME_FORMAT
import json_classes
from logic.submissions import (
    submit_assignment as logic_submit_assignment,
    get_assignment_submissions as logic_get_assignment_submissions,
    get_submission as logic_get_submission,
    grade_submission as logic_grade_submission,
    create_submission_attachment as logic_create_submission_attachment,
    get_submission_attachments as logic_get_submission_attachments,
    download_submission_attachment as logic_download_submission_attachment,
)


router = APIRouter()


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
        return logic_submit_assignment(db_conn, db_cursor, course_id, assignment_id, comment, student_email)


@router.get("/get_assignment_submissions", response_model=List[json_classes.Submission])
async def get_assignment_submissions(course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the list of students submissions of provided assignments.

    Teacher role required.

    Submissions are ordered by submission_time, the first submissions are new.

    Returns the list of submissions (course_id, assignment_id, student_email, student_name, submission_time, last_modification_time, comment, grade, gradedby_email).

    The format of submission_time and last_modification_time is TIME_FORMAT.

    `grade` and `gradedby_email` can be `null` if the assignment was not graded yet.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):
        return logic_get_assignment_submissions(db_cursor, course_id, assignment_id, user_email)


@router.get("/get_submission", response_model=json_classes.Submission)
async def get_submission(
    course_id: str,
    assignment_id: str,
    student_email: str,
    user_email: str = Depends(get_current_user),
):
    """
    Get the student submission of assignment by course_id, assignment_id and student_email.

    - Teacher can get all submissions of the course
    - Parent can get the submission of their student
    - Stuent can get their submissions

    Returns the submission (course_id, assignment_id, student_email, student_name, submission_time, last_modification_time, comment, grade, gradedby_email).

    The format of submission_time and last_modification_time is TIME_FORMAT.

    `grade` and `gradedby_email` can be `null` if the assignment was not graded yet.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):
        return logic_get_submission(db_cursor, course_id, assignment_id, student_email, user_email)


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


@router.post("/create_submission_attachment", response_model=json_classes.SubmissionAttachmentMetadata)
async def create_submission_attachment(
    course_id: str,
    assignment_id: str,
    student_email: str,
    file: UploadFile = File(...),
    user_email: str = Depends(get_current_user),
):
    """
    Attach the provided file to provided course assignment submission.

    Student role required.

    Returns the (course_id, assignment_id, student_email, file_id, filename, upload_time) for the new attachment in case of success.

    The format of upload_time is TIME_FORMAT.
    """
    with get_db() as (db_conn, db_cursor):
        return await logic_create_submission_attachment(db_conn, db_cursor, course_id, assignment_id, student_email, file, user_email)


@router.get("/get_submission_attachments", response_model=List[json_classes.SubmissionAttachmentMetadata])
async def get_submission_attachments(course_id: str, assignment_id: str, student_email: str, user_email: str = Depends(get_current_user)):
    """
    Get the list of attachments to the course assignment submission by provided course_id, assignment_id, student_email.

    Returns list of attachments metadata (course_id, assignment_id, student_email, file_id, filename, upload_time).

    The format of upload_time is TIME_FORMAT.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_get_submission_attachments(db_cursor, course_id, assignment_id, student_email, user_email)


@router.get("/download_submission_attachment")
async def download_submission_attachment(course_id: str, assignment_id: str, student_email: str, file_id: str, user_email: str = Depends(get_current_user)):
    """
    Download the attachment to the course assignment submission by provided course_id, assignment_id, student_email, file_id.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_download_submission_attachment(db_cursor, course_id, assignment_id, student_email, file_id, user_email)
