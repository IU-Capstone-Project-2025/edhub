from fastapi import UploadFile, Response
import edhub_errors
from constants import TIME_FORMAT
import constraints
import sql.assignments as sql_ass
import sql.files as sql_files
import logic.logging as logger
from logic.uploading import careful_upload


def create_assignment(
    db_conn,
    course_id: str,
    title: str,
    description: str,
    user_email: str,
):
    with db_conn.cursor() as db_cursor:
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        assignment_id = sql_ass.insert_assignment(db_cursor, course_id, title, description, user_email)
        db_conn.commit()

        logger.log(db_conn, logger.TAG_ASSIGNMENT_ADD, f"Created assignment {assignment_id}")

        return {"course_id": course_id, "assignment_id": assignment_id}


def remove_assignment(db_conn, course_id: str, assignment_id: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        sql_ass.delete_assignment(db_cursor, course_id, assignment_id)
        db_conn.commit()

        logger.log(db_conn, logger.TAG_ASSIGNMENT_DEL, f"Removed assignment {assignment_id}")

        return {"success": True}


def get_assignment(db_conn, course_id: str, assignment_id: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_course_access(db_cursor, user_email, course_id)
        constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
        assignment = sql_ass.select_assignment(db_cursor, course_id, assignment_id)

        res = {
            "course_id": str(assignment[0]),
            "assignment_id": assignment[1],
            "creation_time": assignment[2].strftime(TIME_FORMAT),
            "title": assignment[3],
            "description": assignment[4],
            "author": assignment[5],
        }
        return res


async def create_assignment_attachment(
    db_conn, storage_db_conn, course_id: str, assignment_id: str, file: UploadFile, user_email: str
):
    with db_conn.cursor() as db_cursor, storage_db_conn.cursor() as storage_db_cursor:
        constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        contents = await careful_upload(file)

        attachment_metadata = sql_ass.insert_assignment_attachment(
            db_cursor, storage_db_cursor, course_id, assignment_id, file.filename, contents
        )
        db_conn.commit()
        storage_db_conn.commit()

        logger.log(
            db_conn,
            logger.TAG_ATTACHMENT_ADD_ASS,
            f"User {user_email} created an attachment {file.filename} for the assignment {assignment_id} in course {course_id}",
        )
        return {
            "course_id": course_id,
            "assignment_id": assignment_id,
            "file_id": attachment_metadata[0],
            "filename": file.filename,
            "upload_time": attachment_metadata[1].strftime(TIME_FORMAT),
        }


def get_assignment_attachments(db_conn, course_id: str, assignment_id: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
        constraints.assert_course_access(db_cursor, user_email, course_id)

        files = sql_ass.select_assignment_attachments(db_cursor, course_id, assignment_id)

        res = [
            {
                "course_id": course_id,
                "assignment_id": assignment_id,
                "file_id": file[0],
                "filename": file[1],
                "upload_time": file[2].strftime(TIME_FORMAT),
            }
            for file in files
        ]

        return res


def download_assignment_attachment(
    db_conn, storage_db_conn, course_id: str, assignment_id: str, file_id: str, user_email: str
):
    with db_conn.cursor() as db_cursor, storage_db_conn.cursor() as storage_db_cursor:
        constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
        constraints.assert_course_access(db_cursor, user_email, course_id)

        file = sql_files.download_attachment(storage_db_cursor, file_id)
        if not file:
            raise edhub_errors.AttachmentNotFoundException(file_id)

        return Response(
            content=file[0],
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{file[1]}"'},
        )


def get_all_assignments(db_conn, course_id: str, user_email: str) -> list[int]:
    with db_conn.cursor() as db_cursor:
        constraints.assert_course_access(db_cursor, user_email, course_id)
        return sql_ass.sql_get_all_assignments(db_cursor, course_id)
