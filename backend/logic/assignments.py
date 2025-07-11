from fastapi import UploadFile, Response
import edhub_errors
from constants import TIME_FORMAT
import constraints
import sql.assignments as sql_ass
import sql.files as sql_files
from logic.uploading import careful_upload
from sql.dto import AssignmentDTO, AttachmentInfoDTO
from datetime import datetime


def create_assignment(conn, course_id: str, title: str, description: str) -> int:
    """
    Returns the ID of the new assignment within the course.
    """
    constraints.assert_course_exists(conn, course_id)
    assignment_id = sql_ass.insert_assignment(conn, course_id, title, description, user_email)
    return assignment_id


def remove_assignment(conn, course_id: str, assignment_id: str) -> None:
    constraints.assert_assignment_exists(conn, course_id, assignment_id)
    sql_ass.delete_assignment(conn, course_id, assignment_id)


def get_assignment(conn, course_id: str, assignment_id: str) -> AssignmentDTO:
    constraints.assert_assignment_exists(conn, course_id, assignment_id)
    assignment = sql_ass.select_assignment(conn, course_id, assignment_id)
    return assignment


def create_assignment_attachment(
    conn, storage_db_conn, course_id: str, assignment_id: str, filename: str, file_contents: bytes
) -> tuple[str, datetime]:
    """
    Returns the pair `(fileID, uploadtime)`
    """
    constraints.assert_assignment_exists(conn, course_id, assignment_id)
    attachment_metadata = sql_ass.insert_assignment_attachment(
        conn, storage_db_conn, course_id, assignment_id, filename, file_contents
    )
    return attachment_metadata


def get_assignment_attachments(conn, course_id: str, assignment_id: str) -> list[AttachmentInfoDTO]:
    constraints.assert_assignment_exists(conn, course_id, assignment_id)
    return sql_ass.select_assignment_attachments(conn, course_id, assignment_id)


def download_assignment_attachment(
    conn, storage_conn, course_id: str, assignment_id: str, file_id: str
) -> tuple[AttachmentInfoDTO, bytes]:
    """
    Returns the content of the file along with its metadata
    """
    constraints.assert_assignment_attachment_exists(conn, course_id, assignment_id)
    constraints.assert_file_exists(storage_conn, file_id)
    metadata = sql_ass.select_single_assignment_attachment(conn, course_id, assignment_id, file_id)
    content = sql_files.download_attachment(storage_conn, file_id)
    return metadata, content
