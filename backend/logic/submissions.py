from fastapi import HTTPException, UploadFile, Response
from constants import TIME_FORMAT
import constraints
import repo.submissions as repo_submit
import repo.files as repo_files
import logic.logging as logger
from logic.uploading import careful_upload


def submit_assignment(
    db_conn,
    db_cursor,
    course_id: str,
    assignment_id: str,
    comment: str,
    student_email: str,
):

    # checking constraints
    constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
    constraints.assert_student_access(db_cursor, student_email, course_id)

    submission = repo_submit.sql_select_submission_grade(db_cursor, course_id, assignment_id, student_email)

    # inserting submission
    if submission is None:
        repo_submit.sql_insert_submission(db_cursor, course_id, assignment_id, student_email, comment)
        db_conn.commit()

    # updating submission if not graded
    elif submission and submission[0] in (None, "null"):
        repo_submit.sql_update_submission_comment(db_cursor, comment, course_id, assignment_id, student_email)
        db_conn.commit()

    else:
        raise HTTPException(status_code=404, detail="Can't edit the submission after it was graded.")

    logger.log(db_conn, logger.TAG_ASSIGNMENT_SUBMIT, f"Student {student_email} submitted an assignment{assignment_id} in {course_id}")

    return {"success": True}


def get_assignment_submissions(db_cursor, course_id: str, assignment_id: str, user_email: str):
    # checking constraints
    constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # finding students' submissions
    submissions = repo_submit.sql_select_submissions(db_cursor, course_id, assignment_id)

    res = [
        {
            "course_id": course_id,
            "assignment_id": assignment_id,
            "student_email": sub[0],
            "student_name": sub[1],
            "submission_time": sub[2].strftime(TIME_FORMAT),
            "last_modification_time": sub[3].strftime(TIME_FORMAT),
            "comment": sub[4],
            "grade": sub[5],
            "gradedby_email": sub[6],
        }
        for sub in submissions
    ]
    return res


def get_submission(
    db_cursor,
    course_id: str,
    assignment_id: str,
    student_email: str,
    user_email: str,
):
    # checking constraints
    constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
    constraints.assert_student_access(db_cursor, student_email, course_id)
    if not (
        constraints.check_teacher_access(db_cursor, user_email, course_id)
        or constraints.check_parent_student_access(db_cursor, user_email, student_email, course_id)
        or student_email == user_email
    ):
        raise HTTPException(status_code=403, detail="User does not have access to this submission")

    # finding student's submission
    submission = repo_submit.sql_select_single_submission(db_cursor, course_id, assignment_id, student_email)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission of this user is not found")

    res = {
        "course_id": course_id,
        "assignment_id": assignment_id,
        "student_email": submission[0],
        "student_name": submission[1],
        "submission_time": submission[2].strftime(TIME_FORMAT),
        "last_modification_time": submission[3].strftime(TIME_FORMAT),
        "comment": submission[4],
        "grade": submission[5],
        "gradedby_email": submission[6],
    }
    return res


def grade_submission(
    db_conn,
    db_cursor,
    course_id: str,
    assignment_id: str,
    student_email: str,
    grade: str,
    user_email: str,
):
    # checking constraints
    constraints.assert_teacher_access(db_cursor, user_email, course_id)
    constraints.assert_submission_exists(db_cursor, course_id, assignment_id, student_email)

    repo_submit.sql_update_submission_grade(db_cursor, grade, user_email, course_id, assignment_id, student_email)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_ASSIGNMENT_GRADE, f"Teacher {user_email} graded an assignment {assignment_id} in {course_id} by {student_email}")

    return {"success": True}


async def create_submission_attachment(db_conn, db_cursor, storage_db_conn, storage_db_cursor, course_id: str, assignment_id: str, student_email: str, file: UploadFile, user_email: str):
    # checking constraints
    constraints.assert_submission_exists(db_cursor, course_id, assignment_id, student_email)
    if student_email != user_email:
        raise HTTPException(status_code=403, detail="User does not have access to this submission")

    # read the file
    contents = await careful_upload(file)

    # save the file into database
    attachment_metadata = repo_submit.sql_insert_submission_attachment(db_cursor, storage_db_cursor, course_id, assignment_id, student_email, file.filename, contents)
    db_conn.commit()
    storage_db_conn.commit()

    logger.log(db_conn, logger.TAG_ATTACHMENT_ADD_SUB, f"User {user_email} created an attachment {file.filename} for the submission for the assignment {assignment_id} in course {course_id}")
    return {
        "course_id": course_id,
        "assignment_id": assignment_id,
        'student_email': student_email,
        'file_id': attachment_metadata[0],
        'filename' : file.filename,
        'upload_time' : attachment_metadata[1].strftime(TIME_FORMAT)
    }


def get_submission_attachments(db_cursor, course_id: str, assignment_id: str, student_email: str, user_email: str):
    # checking constraints
    constraints.assert_submission_exists(db_cursor, course_id, assignment_id, student_email)
    if not (
        constraints.check_teacher_access(db_cursor, user_email, course_id)
        or constraints.check_parent_student_access(db_cursor, user_email, student_email, course_id)
        or student_email == user_email
    ):
        raise HTTPException(status_code=403, detail="User does not have access to this submission")

    # searching for submission attachments
    files = repo_submit.sql_select_submission_attachments(db_cursor, course_id, assignment_id, student_email)

    res = [{
        "course_id": course_id,
        "assignment_id": assignment_id,
        'student_email': student_email,
        "file_id": file[0],
        "filename": file[1],
        "upload_time": file[2].strftime(TIME_FORMAT)
    } for file in files]
 
    return res


def download_submission_attachment(db_cursor, storage_db_cursor, course_id: str, assignment_id: str, student_email: str, file_id: str, user_email: str):
    # checking constraints
    constraints.assert_submission_exists(db_cursor, course_id, assignment_id, student_email)
    if not (
        constraints.check_teacher_access(db_cursor, user_email, course_id)
        or constraints.check_parent_student_access(db_cursor, user_email, student_email, course_id)
        or student_email == user_email
    ):
        raise HTTPException(status_code=403, detail="User does not have access to this submission")

    # searching for submission attachment
    file = repo_files.sql_download_attachment(storage_db_cursor, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Attachment not found")

    return Response(
        content=file[0],
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file[1]}"'}
    )
