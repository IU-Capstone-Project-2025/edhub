from fastapi import Response, APIRouter, Depends, UploadFile, File
from typing import List

import logic.logging as logger
from auth import get_current_user
import json_classes
from logic.assignments import (
    create_assignment as logic_create_assignment,
    remove_assignment as logic_remove_assignment,
    get_assignment as logic_get_assignment,
    create_assignment_attachment as logic_create_assignment_attachment,
    get_assignment_attachments as logic_get_assignment_attachments,
    download_assignment_attachment as logic_download_assignment_attachment,
)
from logic.uploading import careful_upload
import constraints
from constants import TIME_FORMAT

import database


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

    Returns the (course_id, assignment_id) for the new assignment in case of success.
    """
    with database.get_system_conn() as conn:
        constraints.assert_teacher_or_admin_access(conn, user_email, course_id)
        assignment_id = logic_create_assignment(conn, course_id, title, description, user_email)
        logger.log(conn, logger.TAG_ASSIGNMENT_ADD, f"User {user_email} created assignment {assignment_id} in course {course_id}")
        return {"course_id": course_id, "assignment_id": assignment_id}


@router.post("/remove_assignment", response_model=json_classes.Success)
async def remove_assignment(course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)):
    """
    Remove the assignment by the provided course_id and assignment_id.

    Teacher role required.
    """
    with database.get_system_conn() as db_conn:
        constraints.assert_teacher_or_admin_access(db_conn, user_email, course_id)
        logic_remove_assignment(db_conn, course_id, assignment_id)
        logger.log(db_conn, logger.TAG_ASSIGNMENT_DEL, f"User {user_email} removed assignment {assignment_id} in course {course_id}")
        return json_classes.successful


@router.get("/get_assignment", response_model=json_classes.Assignment)
async def get_assignment(course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the assignment details by the provided (course_id, assignment_id).

    Returns course_id, assignment_id, creation_time, title, description, and email of the author.

    Author can be 'null' if the author deleted their account.

    The format of creation time is TIME_FORMAT.
    """
    with database.get_system_conn() as conn:
        constraints.assert_course_access(conn, user_email, course_id)
        assignment = logic_get_assignment(conn, course_id, assignment_id)
    return {
        "course_id": str(assignment[0]),
        "assignment_id": assignment[1],
        "creation_time": assignment[2].strftime(TIME_FORMAT),
        "title": assignment[3],
        "description": assignment[4],
        "author": assignment[5],
    }


@router.post("/create_assignment_attachment", response_model=json_classes.AssignmentAttachmentMetadata)
async def create_assignment_attachment(
    course_id: str,
    assignment_id: str,
    file: UploadFile = File(...),
    user_email: str = Depends(get_current_user),
):
    """
    Attach the provided file to provided course assignment.

    Teacher role required.

    Returns the (course_id, assignment_id, file_id, filename, upload_time) for the new attachment in case of success.

    The format of upload_time is TIME_FORMAT.
    """
    with database.get_system_conn() as db_conn, database.get_storage_conn() as storage_db_conn:
        constraints.assert_teacher_or_admin_access(db_conn, user_email, course_id)
        contents = await careful_upload(file)
        fileid, uploadtime = logic_create_assignment_attachment(
            db_conn, storage_db_conn, course_id, assignment_id, contents
        )
        logger.log(
            db_conn,
            logger.TAG_ATTACHMENT_ADD_ASS,
            f"User {user_email} created an attachment {file.filename} for the assignment {assignment_id} in course {course_id}",
        )
    return {
        "course_id": course_id,
        "assignment_id": assignment_id,
        "file_id": fileid,
        "filename": file.filename,
        "upload_time": uploadtime.strftime(TIME_FORMAT),
    }


@router.get("/get_assignment_attachments", response_model=List[json_classes.AssignmentAttachmentMetadata])
async def get_assignment_attachments(course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the list of course assignment attachments by provided course_id, assignment_id.

    Returns list of attachments metadata (course_id, assignment_id, file_id, filename, upload_time).

    The format of upload_time is TIME_FORMAT.
    """
    with database.get_system_conn() as db_conn:
        constraints.assert_course_access(db_conn, user_email, course_id)
        files = logic_get_assignment_attachments(db_conn, course_id, assignment_id)
        return [
            {
                "course_id": course_id,
                "assignment_id": assignment_id,
                "file_id": file.fileid,
                "filename": file.filename,
                "upload_time": file.uploadtime.strftime(TIME_FORMAT),
            }
            for file in files
        ]


@router.get("/download_assignment_attachment")
async def download_assignment_attachment(
    course_id: str, assignment_id: str, file_id: str, user_email: str = Depends(get_current_user)
):
    """
    Download the course assignment attachment by provided course_id, assignment_id, file_id.
    """
    with database.get_system_conn() as db_conn, database.get_storage_conn() as storage_db_conn:
        constraints.assert_course_access(db_conn, user_email, course_id)
        metadata, content = logic_download_assignment_attachment(
            db_conn, storage_db_conn, course_id, assignment_id, file_id
        )
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{metadata.filename}"'},
    )
