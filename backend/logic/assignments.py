from fastapi import HTTPException, UploadFile, Response
from constants import TIME_FORMAT
import constraints
import repo.assignments as repo_ass
import logic.logging as logger
from logic.uploading import careful_upload


def create_assignment(
    db_conn,
    db_cursor,
    course_id: str,
    title: str,
    description: str,
    user_email: str,
):
    # checking constraints
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # create assignment
    assignment_id = repo_ass.sql_insert_assignment(db_cursor, course_id, title, description, user_email)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_ASSIGNMENT_ADD, f"Created assignment {assignment_id}")

    return {"course_id": course_id, "assignment_id": assignment_id}


def remove_assignment(db_conn, db_cursor, course_id: str, assignment_id: str, user_email: str):
    # checking constraints
    constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # remove assignment
    repo_ass.sql_delete_assignment(db_cursor, course_id, assignment_id)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_ASSIGNMENT_DEL, f"Removed assignment {assignment_id}")

    return {"success": True}


def get_assignment(db_cursor, course_id: str, assignment_id: str, user_email: str):

    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # searching for assignments
    assignment = repo_ass.sql_select_assignment(db_cursor, course_id, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    res = {
        "course_id": str(assignment[0]),
        "assignment_id": assignment[1],
        "creation_time": assignment[2].strftime(TIME_FORMAT),
        "title": assignment[3],
        "description": assignment[4],
        "author": assignment[5],
    }
    return res


async def create_assignment_attachment(db_conn, db_cursor, course_id: str, assignment_id: str, file: UploadFile, user_email: str):
    # checking constraints
    constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # read the file
    contents = await careful_upload(file)

    # save the file into database
    attachment_metadata = repo_ass.sql_insert_assignment_attachment(db_cursor, course_id, assignment_id, file.filename, contents)
    db_conn.commit()

    # TODO: logger for the attachment (Askar)
    # logger.log(db_conn, logger.TAG_assignment_ADD, f"User {user_email} attached a file {file.filename} to the assignment assignment {assignment_id} in course {course_id}")
    return {
        "course_id": course_id,
        "assignment_id": assignment_id,
        'file_id': attachment_metadata[0],
        'filename' : file.filename,
        'upload_time' : attachment_metadata[1].strftime(TIME_FORMAT)
    }


def get_assignment_attachments(db_cursor, course_id: str, assignment_id: str, user_email: str):
    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # searching for assignment attachments
    files = repo_ass.sql_select_assignment_attachments(db_cursor, course_id, assignment_id)

    res = [{
        "course_id": course_id,
        "assignment_id": assignment_id,
        "file_id": file[0],
        "filename": file[1],
        "upload_time": file[2].strftime(TIME_FORMAT)
    } for file in files]
 
    return res


def download_assignment_attachment(db_cursor, course_id: str, assignment_id: str, file_id: str, user_email: str):
    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # searching for assignment attachment
    file = repo_ass.sql_download_assignment_attachment(db_cursor, course_id, assignment_id, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Attachment not found")

    return Response(
        content=file[0],
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file[1]}"'}
    )
