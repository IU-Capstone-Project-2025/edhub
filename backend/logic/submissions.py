from fastapi import UploadFile, Response
import edhub_errors
import constraints
import sql.submissions as sql_submit
import sql.files as sql_files
from sql.dto import SubmissionDTO
from datetime import datetime
from sql.dto import AttachmentInfoDTO


def submit_assignment(
    conn,
    course_id: str,
    assignment_id: str,
    comment: str,
    student_email: str,
) -> None:
    constraints.assert_assignment_exists(conn, course_id, assignment_id)
    if not constraints.check_submission_exists(conn, course_id, assignment_id, student_email):
        sql_submit.insert_submission(conn, course_id, assignment_id, student_email, comment)
        return

    grade = sql_submit.select_submission_grade(conn, course_id, assignment_id, student_email)
    if grade is None:
        sql_submit.update_submission_comment(conn, comment, course_id, assignment_id, student_email)
        return
    raise edhub_errors.CannotEditGradedSubmissionException()


def get_assignment_submissions(db_conn, course_id: str, assignment_id: str) -> list[SubmissionDTO]:
    constraints.assert_assignment_exists(db_conn, course_id, assignment_id)
    return sql_submit.select_submissions(db_conn, course_id, assignment_id)


def get_submission(
    conn,
    course_id: str,
    assignment_id: str,
    student_email: str,
) -> SubmissionDTO:
    constraints.assert_submission_exists(conn, course_id, assignment_id, student_email)
    return sql_submit.select_single_submission(conn, course_id, assignment_id, student_email)


def grade_submission(
    db_conn,
    course_id: str,
    assignment_id: str,
    student_email: str,
    grade: str,
    grader_email: str,
) -> None:
    constraints.assert_submission_exists(db_conn, course_id, assignment_id, student_email)
    sql_submit.update_submission_grade(db_conn, grade, grader_email, course_id, assignment_id, student_email)


def create_submission_attachment(
    conn,
    storage_conn,
    course_id: str,
    assignment_id: str,
    student_email: str,
    filename: str,
    contents: bytes
) -> tuple[str, datetime]:
    constraints.assert_submission_exists(conn, course_id, assignment_id, student_email)
    if sql_submit.select_submission_grade(conn, course_id, assignment_id, student_email) is not None:
        raise edhub_errors.CannotEditGradedSubmissionException()
    return sql_submit.insert_submission_attachment(
        conn, storage_conn, course_id, assignment_id, student_email, filename, contents
    )


def get_submission_attachments(conn, course_id: str, assignment_id: str, student_email: str) -> list[AttachmentInfoDTO]:
    constraints.assert_submission_exists(conn, course_id, assignment_id, student_email)
    return sql_submit.select_submission_attachments(conn, course_id, assignment_id, student_email)


def download_submission_attachment(
    conn, storage_conn, course_id: str, assignment_id: str, student_email: str, file_id: str
) -> tuple[AttachmentInfoDTO, bytes]:
    constraints.assert_submission_attachment_exists(conn, course_id, assignment_id, student_email)
    constraints.assert_file_exists(storage_conn, file_id)
    content = sql_files.download_attachment(storage_conn, file_id)
    metadata = sql_submit.select_single_submission_attachment(conn, course_id, assignment_id, student_email, file_id)
    return metadata, content
