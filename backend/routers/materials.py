from fastapi import Response, APIRouter, Depends, UploadFile, File
from typing import List
from constants import TIME_FORMAT
import constraints

from auth import get_current_user
import json_classes
from logic.materials import (
    create_material as logic_create_material,
    remove_material as logic_remove_material,
    get_material as logic_get_material,
    create_material_attachment as logic_create_material_attachment,
    get_material_attachments as logic_get_material_attachments,
    download_material_attachment as logic_download_material_attachment,
)
import logic.logging as logger
from logic.uploading import careful_upload
from sql.dto import AttachmentInfoDTO

import database

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
    with database.get_system_conn() as db_conn:
        constraints.assert_teacher_or_admin_access(db_conn, user_email, course_id)
        matid = logic_create_material(db_conn, course_id, title, description, user_email)
        logger.log(
            db_conn, logger.TAG_MATERIAL_ADD, f"User {user_email} created a material {matid} in {course_id}"
        )
    return {"material_id": matid, "course_id": course_id}


@router.post("/remove_material", response_model=json_classes.Success)
async def remove_material(course_id: str, material_id: str, user_email: str = Depends(get_current_user)):
    """
    Remove the material by the provided course_id and material_id.

    Teacher role required.
    """
    with database.get_system_conn() as db_conn:
        constraints.assert_material_exists(db_conn, course_id, material_id)
        constraints.assert_teacher_or_admin_access(db_conn, user_email, course_id)
        logic_remove_material(db_conn, course_id, material_id, user_email)
        logger.log(
            db_conn, logger.TAG_MATERIAL_DEL, f"User {user_email} removed a material {material_id} in {course_id}"
        )
        return json_classes.Success()


@router.get("/get_material", response_model=json_classes.Material)
async def get_material(course_id: str, material_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the material details by the provided (course_id, material_id).

    Returns course_id, material_id, creation_time, title, description, and email of the author.

    Author can be 'null' if the author deleted their account.

    The format of creation time is TIME_FORMAT.
    """
    with database.get_system_conn() as db_conn:
        constraints.assert_course_access(db_conn, user_email, course_id)
        constraints.assert_material_exists(db_conn, course_id, material_id)
        mat = logic_get_material(db_conn, course_id, material_id, user_email)
        return {
            "course_id": mat.course_id,
            "material_id": mat.material_id,
            "creation_time": mat.timeadded.strftime(TIME_FORMAT),
            "title": mat.name,
            "description": mat.description,
            "author": mat.author_email
        }


@router.post("/create_material_attachment", response_model=json_classes.MaterialAttachmentMetadata)
async def create_material_attachment(
    course_id: str,
    material_id: str,
    file: UploadFile = File(...),
    user_email: str = Depends(get_current_user),
):
    """
    Attach the provided file to provided course material.

    Teacher role required.

    Returns the (course_id, material_id, file_id, filename, upload_time) for the new attachment in case of success.

    The format of upload_time is TIME_FORMAT.
    """
    with database.get_system_conn() as db_conn:
        constraints.assert_material_exists(db_conn, course_id, material_id)
        constraints.assert_teacher_or_admin_access(db_conn, user_email, course_id)
    file_content = careful_upload(file)
    with database.get_system_conn() as db_conn, database.get_storage_conn() as storage_db_conn:
        att = logic_create_material_attachment(
            db_conn, storage_db_conn, course_id, material_id, file.filename, file_content
        )
        logger.log(
            db_conn,
            logger.TAG_ATTACHMENT_ADD_MAT,
            f"User {user_email} created an attachment {file.filename} for the material {material_id} in course {course_id}",
        )
    return {
        "course_id": course_id,
        "material_id": material_id,
        "file_id": att[0],
        "filename": file.filename,
        "upload_time": att[1].strftime(TIME_FORMAT),
    }


@router.get("/get_material_attachments", response_model=List[json_classes.MaterialAttachmentMetadata])
async def get_material_attachments(course_id: str, material_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the list of course material attachments by provided course_id, material_id.

    Returns list of attachments metadata (course_id, material_id, file_id, filename, upload_time).

    The format of upload_time is TIME_FORMAT.
    """
    with database.get_system_conn() as db_conn:
        constraints.assert_material_exists(db_conn, course_id, material_id)
        constraints.assert_course_access(db_conn, user_email, course_id)
        atts: list[AttachmentInfoDTO]
        atts = logic_get_material_attachments(db_conn, course_id, material_id, user_email)
        return [
            {
                "course_id": course_id,
                "material_id": material_id,
                "file_id": att.fileid,
                "filename": att.filename,
                "upload_time": att.timeadded.strftime(TIME_FORMAT),
            }
            for att in atts
        ]


@router.get("/download_material_attachment")
async def download_material_attachment(
    course_id: str, material_id: str, file_id: str, user_email: str = Depends(get_current_user)
):
    """
    Download the course material attachment by provided course_id, material_id, file_id.
    """
    with database.get_system_conn() as db_conn, database.get_storage_conn() as storage_db_conn:
        constraints.assert_course_access(db_conn, user_email, course_id)
        metadata, content = logic_download_material_attachment(
            db_conn, storage_db_conn, course_id, material_id, file_id
        )
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{metadata.filename}"'},
    )
