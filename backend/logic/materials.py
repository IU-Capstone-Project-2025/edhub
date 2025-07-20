from fastapi import HTTPException, UploadFile, Response
from constants import TIME_FORMAT
import constraints
import repo.materials as repo_mat
import repo.files as repo_files
import logic.logging as logger
from logic.uploading import careful_upload


def create_material(db_conn, db_cursor, course_id: str, title: str, description: str, user_email: str):
    # checking constraints
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # create material
    material_id = repo_mat.sql_insert_material(db_cursor, course_id, title, description, user_email)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_MATERIAL_ADD, f"User {user_email} created a material {material_id} in {course_id}")
    return {"course_id": course_id, "material_id": material_id}


def remove_material(db_conn, db_cursor, course_id: str, material_id: str, user_email: str):
    # checking constraints
    constraints.assert_material_exists(db_cursor, course_id, material_id)
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # remove material
    repo_mat.sql_delete_material(db_cursor, course_id, material_id)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_MATERIAL_DEL, f"User {user_email} removed a material {material_id} in {course_id}")

    return {"success": True}


def get_material(db_cursor, course_id: str, material_id: str, user_email: str):
    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # searching for materials
    material = repo_mat.sql_select_material(db_cursor, course_id, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    res = {
        "course_id": str(material[0]),
        "material_id": material[1],
        "creation_time": material[2].strftime(TIME_FORMAT),
        "title": material[3],
        "description": material[4],
        "author": material[5],
    }
    return res


async def create_material_attachment(db_conn, db_cursor, storage_db_conn, storage_db_cursor, course_id: str, material_id: str, file: UploadFile, user_email: str):
    # checking constraints
    constraints.assert_material_exists(db_cursor, course_id, material_id)
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # read the file
    contents = await careful_upload(file)

    # save the file into database
    attachment_metadata = repo_mat.sql_insert_material_attachment(db_cursor, storage_db_cursor, course_id, material_id, file.filename, contents)
    db_conn.commit()
    storage_db_conn.commit()

    logger.log(db_conn, logger.TAG_ATTACHMENT_ADD_MAT, f"User {user_email} created an attachment {file.filename} for the material {material_id} in course {course_id}")
    return {
        "course_id": course_id,
        "material_id": material_id,
        'file_id': attachment_metadata[0],
        'filename' : file.filename,
        'upload_time' : attachment_metadata[1].strftime(TIME_FORMAT)
    }


def get_material_attachments(db_cursor, course_id: str, material_id: str, user_email: str):
    # checking constraints
    constraints.assert_material_exists(db_cursor, course_id, material_id)
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # searching for material attachments
    files = repo_mat.sql_select_material_attachments(db_cursor, course_id, material_id)

    res = [{
        "course_id": course_id,
        "material_id": material_id,
        "file_id": file[0],
        "filename": file[1],
        "upload_time": file[2].strftime(TIME_FORMAT)
    } for file in files]
 
    return res


def download_material_attachment(db_cursor, storage_db_cursor, course_id: str, material_id: str, file_id: str, user_email: str):
    # checking constraints
    constraints.assert_material_exists(db_cursor, course_id, material_id)
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # searching for material attachment
    file = repo_files.sql_download_attachment(storage_db_cursor, file_id)
    file_metadata = repo_mat.sql_select_material_attachments(db_cursor, course_id, material_id)
    if (not file or not file_metadata):
        raise HTTPException(status_code=404, detail="Attachment not found")

    return Response(
        content=file,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_metadata[1]}"'}
    )
