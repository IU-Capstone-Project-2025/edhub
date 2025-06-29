from fastapi import APIRouter, Depends, UploadFile, File
from typing import List
from constants import TIME_FORMAT

from auth import get_current_user, get_db
import json_classes
from logic.materials import (
    create_material as logic_create_material,
    remove_material as logic_remove_material,
    get_material as logic_get_material,
    create_material_attachment as logic_create_material_attachment,
    get_material_attachments as logic_get_material_attachments,
    download_material_attachment as logic_download_material_attachment
)

router = APIRouter()


@router.post("/create_material", response_model=json_classes.MaterialID)
async def create_material(
    course_id: str,
    title: str,
    description: str,
    user_email: str = Depends(get_current_user),
):
    """
    Create the material with provided title and description in the course with provided course_id.

    Teacher role required.

    Returns the (course_id, material_id) for the new material in case of success.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_create_material(db_conn, db_cursor, course_id, title, description, user_email)


@router.post("/remove_material", response_model=json_classes.Success)
async def remove_material(course_id: str, material_id: str, user_email: str = Depends(get_current_user)):
    """
    Remove the material by the provided course_id and material_id.

    Teacher role required.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_remove_material(db_conn, db_cursor, course_id, material_id, user_email)


@router.get("/get_material", response_model=json_classes.Material)
async def get_material(course_id: str, material_id: str, user_email: str = Depends(get_current_user)):
    f"""
    Get the material details by the provided (course_id, material_id).

    Returns course_id, material_id, creation_time, title, description, and email of the author.

    Author can be 'null' if the author deleted their account.

    The format of creation time is "{TIME_FORMAT}".
    """
    with get_db() as (db_conn, db_cursor):
        return logic_get_material(db_cursor, course_id, material_id, user_email)


@router.post("/create_material_attachment", response_model=json_classes.MaterialAttachmentMetadata)
async def create_material_attachment(
    course_id: str,
    material_id: str,
    file: UploadFile = File(...),
    user_email: str = Depends(get_current_user),
):
    f"""
    Attach the provided file to the attached course material.

    Teacher role required.

    Returns the (course_id, material_id, file_id, filename, upload_time) for the new attachment in case of success.

    The format of upload_time is "{TIME_FORMAT}".
    """
    with get_db() as (db_conn, db_cursor):
        return await logic_create_material_attachment(db_conn, db_cursor, course_id, material_id, file, user_email)


@router.get("/get_material_attachments", response_model=List[json_classes.MaterialAttachmentMetadata])
async def get_material_attachments(course_id: str, material_id: str, user_email: str = Depends(get_current_user)):
    f"""
    Get the list of course material attachments by provided course_id, material_id.

    Returns list of attachments metadata (course_id, material_id, file_id, filename, upload_time).

    The format of upload_time is "{TIME_FORMAT}".
    """
    with get_db() as (db_conn, db_cursor):
        return logic_get_material_attachments(db_cursor, course_id, material_id, user_email)


@router.get("/download_material_attachment")
async def download_material_attachment(course_id: str, material_id: str, file_id: str, user_email: str = Depends(get_current_user)):
    f"""
    Download the course material attachment by provided course_id, material_id, file_id.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_download_material_attachment(db_cursor, course_id, material_id, file_id, user_email)