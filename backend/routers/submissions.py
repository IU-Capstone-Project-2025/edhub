from fastapi import Response, APIRouter, Depends, UploadFile, File
from typing import List

from auth import get_current_user
import database
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
import logic.logging as logger
from logic.uploading import careful_upload
from constants import TIME_FORMAT
import edhub_errors
import constraints

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

    Student cannot submit to an already graded assignment.
    """
    with database.get_system_conn() as conn:
        constraints.assert_student_or_admin_access(conn, student_email, course_id)
        logic_submit_assignment(conn, course_id, assignment_id, comment, student_email)
        logger.log(
            conn,
            logger.TAG_ASSIGNMENT_SUBMIT,
            f"Student {student_email} submitted an assignment {assignment_id} in {course_id}",
        )
    return json_classes.successful


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
    with database.get_system_conn() as conn:
        constraints.assert_teacher_or_admin_access(conn, user_email, course_id)
        subs = logic_get_assignment_submissions(conn, course_id, assignment_id)
        return [
            {
                "course_id": course_id,
                "assignment_id": assignment_id,
                "student_email": sub.email,
                "student_name": sub.publicname,
                "submission_time": sub.timeadded.strftime(TIME_FORMAT),
                "last_modification_time": sub.timemodified.strftime(TIME_FORMAT),
                "comment": sub.comment,
                "grade": sub.grade,
                "gradedby_email": sub.gradedby,
            }
            for sub in subs
        ]


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
    with database.get_system_conn() as conn:
        if not (
            constraints.check_teacher_or_admin_access(conn, user_email, course_id)
            or constraints.check_parent_student_access(conn, user_email, student_email, course_id)
            or student_email == user_email
        ):
            raise edhub_errors.NoAccessToSubmissionException(course_id, student_email, user_email)
        sub = logic_get_submission(conn, course_id, assignment_id, student_email)
    return {
        "course_id": course_id,
        "assignment_id": assignment_id,
        "student_email": sub.email,
        "student_name": sub.publicname,
        "submission_time": sub.timeadded.strftime(TIME_FORMAT),
        "last_modification_time": sub.timemodified.strftime(TIME_FORMAT),
        "comment": sub.comment,
        "grade": sub.grade,
        "gradedby_email": sub.gradedby,
    }


@router.post("/grade_submission", response_model=json_classes.Success)
async def grade_submission(
    course_id: str,
    assignment_id: str,
    student_email: str,
    grade: str,
    user_email: str = Depends(get_current_user),
):
    """
    Grade a student's submission.

    Teacher role required.
    """
    with database.get_system_conn() as conn:
        constraints.assert_teacher_or_admin_access(conn, user_email, course_id)
        logic_grade_submission(conn, course_id, assignment_id, student_email, grade, user_email)
        logger.log(
            conn,
            logger.TAG_ASSIGNMENT_GRADE,
            f"Teacher {user_email} graded an assignment {assignment_id} in {course_id} by {student_email}",
        )
    return json_classes.successful


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
    with database.get_system_conn() as db_conn, database.get_storage_conn() as storage_db_conn:
        if student_email != user_email:
            raise edhub_errors.CannotEditOthersSubmissionException(user_email, student_email)
        contents = await careful_upload(file)
        res = logic_create_submission_attachment(
            db_conn, storage_db_conn, course_id, assignment_id, student_email, file.filename, contents
        )
        logger.log(
            db_conn,
            logger.TAG_ATTACHMENT_ADD_SUB,
            f"User {user_email} created an attachment {file.filename} for the submission for the assignment {assignment_id} in course {course_id}",
        )
    return {
        "course_id": course_id,
        "assignment_id": assignment_id,
        "student_email": student_email,
        "file_id": res[0],
        "filename": file.filename,
        "upload_time": res[1].strftime(TIME_FORMAT),
    }


@router.get("/get_submission_attachments", response_model=List[json_classes.SubmissionAttachmentMetadata])
async def get_submission_attachments(
    course_id: str, assignment_id: str, student_email: str, user_email: str = Depends(get_current_user)
):
    """
    Get the list of attachments to the course assignment submission by provided course_id, assignment_id, student_email.

    Returns list of attachments metadata (course_id, assignment_id, student_email, file_id, filename, upload_time).

    The format of upload_time is TIME_FORMAT.
    """
    with database.get_system_conn() as conn:
        if not (
            constraints.check_teacher_access(conn, user_email, course_id)
            or constraints.check_parent_student_access(conn, user_email, student_email, course_id)
            or student_email == user_email
        ):
            raise edhub_errors.NoAccessToSubmissionException(course_id, user_email, student_email)
        atts = logic_get_submission_attachments(conn, course_id, assignment_id, student_email)
    return [
        {
            "course_id": course_id,
            "assignment_id": assignment_id,
            "student_email": student_email,
            "file_id": file.fileid,
            "filename": file.filename,
            "upload_time": file.uploadtime.strftime(TIME_FORMAT),
        }
        for file in atts
    ]


@router.get("/download_submission_attachment")
async def download_submission_attachment(
    course_id: str, assignment_id: str, student_email: str, file_id: str, user_email: str = Depends(get_current_user)
):
    """
    Download the attachment to the course assignment submission by provided course_id, assignment_id, student_email, file_id.
    """
    with database.get_system_conn() as conn, database.get_storage_conn() as storage_conn:
        if not (
            constraints.check_teacher_access(conn, user_email, course_id)
            or constraints.check_parent_student_access(conn, user_email, student_email, course_id)
            or student_email == user_email
        ):
            raise edhub_errors.NoAccessToSubmissionException(course_id, user_email, student_email)
        metadata, content = logic_download_submission_attachment(
            conn, storage_conn, course_id, assignment_id, student_email, file_id
        )
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{metadata.filename}"'},
        )
