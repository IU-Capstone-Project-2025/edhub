from fastapi import APIRouter, Depends, UploadFile, File
from typing import List

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
    with database.get_system_conn() as db_conn:
        return logic_create_assignment(db_conn, course_id, title, description, user_email)


@router.post("/remove_assignment", response_model=json_classes.Success)
async def remove_assignment(course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)):
    """
    Remove the assignment by the provided course_id and assignment_id.

    Teacher role required.
    """
    with database.get_system_conn() as db_conn:
        return logic_remove_assignment(db_conn, course_id, assignment_id, user_email)


@router.get("/get_assignment", response_model=json_classes.Assignment)
async def get_assignment(course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the assignment details by the provided (course_id, assignment_id).

    Returns course_id, assignment_id, creation_time, title, description, and email of the author.

    Author can be 'null' if the author deleted their account.

    The format of creation time is TIME_FORMAT.
    """

    with database.get_system_conn() as db_cursor:
        return logic_get_assignment(db_cursor, course_id, assignment_id, user_email)


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
        return await logic_create_assignment_attachment(
            db_conn, storage_db_conn, course_id, assignment_id, file, user_email
        )


@router.get("/get_assignment_attachments", response_model=List[json_classes.AssignmentAttachmentMetadata])
async def get_assignment_attachments(course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the list of course assignment attachments by provided course_id, assignment_id.

    Returns list of attachments metadata (course_id, assignment_id, file_id, filename, upload_time).

    The format of upload_time is TIME_FORMAT.
    """
    with database.get_system_conn() as db_conn:
        return logic_get_assignment_attachments(db_conn, course_id, assignment_id, user_email)


@router.get("/download_assignment_attachment")
async def download_assignment_attachment(
    course_id: str, assignment_id: str, file_id: str, user_email: str = Depends(get_current_user)
):
    """
    Download the course assignment attachment by provided course_id, assignment_id, file_id.
    """
    with database.get_system_conn() as db_conn, database.get_storage_conn() as storage_db_conn:
        return logic_download_assignment_attachment(
            db_conn, storage_db_conn, course_id, assignment_id, file_id, user_email
        )
