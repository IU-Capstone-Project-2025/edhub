from fastapi import UploadFile, Response
import edhub_errors
from constants import TIME_FORMAT
import constraints
import sql.materials as sql_mat
import sql.files as sql_files
import logic.logging as logger
from logic.uploading import careful_upload


def create_material(db_conn, course_id: str, title: str, description: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        material_id = sql_mat.insert_material(db_cursor, course_id, title, description, user_email)
        db_conn.commit()

        logger.log(
            db_conn, logger.TAG_MATERIAL_ADD, f"User {user_email} created a material {material_id} in {course_id}"
        )
        return {"course_id": course_id, "material_id": material_id}


def remove_material(db_conn, course_id: str, material_id: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_material_exists(db_cursor, course_id, material_id)
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        sql_mat.delete_material(db_cursor, course_id, material_id)
        db_conn.commit()

        logger.log(
            db_conn, logger.TAG_MATERIAL_DEL, f"User {user_email} removed a material {material_id} in {course_id}"
        )

        return {"success": True}


def get_material(db_conn, course_id: str, material_id: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_course_access(db_cursor, user_email, course_id)
        constraints.assert_material_exists(db_cursor, course_id, material_id)
        material = sql_mat.select_material(db_cursor, course_id, material_id)

        res = {
            "course_id": str(material[0]),
            "material_id": material[1],
            "creation_time": material[2].strftime(TIME_FORMAT),
            "title": material[3],
            "description": material[4],
            "author": material[5],
        }
        return res


async def create_material_attachment(
    db_conn, storage_db_conn, course_id: str, material_id: str, file: UploadFile, user_email: str
):
    with db_conn.cursor() as db_cursor, storage_db_conn.cursor() as storage_db_cursor:
        constraints.assert_material_exists(db_cursor, course_id, material_id)
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        contents = await careful_upload(file)

        attachment_metadata = sql_mat.insert_material_attachment(
            db_cursor, storage_db_cursor, course_id, material_id, file.filename, contents
        )
        db_conn.commit()
        storage_db_conn.commit()

        logger.log(
            db_conn,
            logger.TAG_ATTACHMENT_ADD_MAT,
            f"User {user_email} created an attachment {file.filename} for the material {material_id} in course {course_id}",
        )
        return {
            "course_id": course_id,
            "material_id": material_id,
            "file_id": attachment_metadata[0],
            "filename": file.filename,
            "upload_time": attachment_metadata[1].strftime(TIME_FORMAT),
        }


def get_material_attachments(db_conn, course_id: str, material_id: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_material_exists(db_cursor, course_id, material_id)
        constraints.assert_course_access(db_cursor, user_email, course_id)

        files = sql_mat.select_material_attachments(db_cursor, course_id, material_id)

        res = [
            {
                "course_id": course_id,
                "material_id": material_id,
                "file_id": file[0],
                "filename": file[1],
                "upload_time": file[2].strftime(TIME_FORMAT),
            }
            for file in files
        ]

        return res


def download_material_attachment(
    db_conn, storage_db_conn, course_id: str, material_id: str, file_id: str, user_email: str
):
    with db_conn.cursor() as db_cursor, storage_db_conn.cursor() as storage_db_cursor:
        constraints.assert_material_exists(db_cursor, course_id, material_id)
        constraints.assert_course_access(db_cursor, user_email, course_id)

        file = sql_files.download_attachment(storage_db_cursor, file_id)
        if not file:
            raise edhub_errors.AttachmentNotFoundException(file_id)

        return Response(
            content=file[0],
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{file[1]}"'},
        )
