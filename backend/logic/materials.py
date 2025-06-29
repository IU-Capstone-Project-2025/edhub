from fastapi import HTTPException, UploadFile
from constants import TIME_FORMAT, ATTACHMENT_SIZE
import constraints
import repo.materials as repo_mat
import logic.logging as logger


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


async def create_material_attachment(db_conn, db_cursor, course_id: str, material_id: str, file: UploadFile, user_email: str):
    # checking constraints
    constraints.assert_material_exists(db_cursor, course_id, material_id)
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # read the file
    contents = await file.read()
    if len(contents) > ATTACHMENT_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 5MB)")

    # save the file into database
    attachment_metadata = repo_mat.sql_insert_material_attachment(db_cursor, course_id, material_id, file.filename, contents)
    db_conn.commit()

    # TODO: logger for the attachment
    # logger.log(db_conn, logger.TAG_MATERIAL_ADD, f"User {user_email} attached a file {file.filename} to the material material {material_id} in course {course_id}")
    return {
        "course_id": course_id,
        "material_id": material_id,
        'file_id': attachment_metadata[0],
        'filename' : file.filename,
        'upload_time' : attachment_metadata[1].strftime(TIME_FORMAT)
    }
