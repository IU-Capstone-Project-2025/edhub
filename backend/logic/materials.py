from fastapi import HTTPException, UploadFile
from typing import List
import os
from constants import TIME_FORMAT, MATERIALS_DIR, MAX_FILE_SIZE
import constraints
import repo.materials as repo_mat


def create_material(db_conn, db_cursor, course_id: str, title: str, description: str, user_email: str):
    # checking constraints
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # create material
    material_id = repo_mat.sql_insert_material(db_cursor, course_id, title, description, user_email)
    db_conn.commit()

    return {"course_id": course_id, "material_id": material_id}


def create_material_attachments(db_conn, db_cursor, course_id: str, material_id: str, user_email: str, files: List[UploadFile]):
    # checking constraints
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # creating a folder
    mat_dir = os.path.join(MATERIALS_DIR, 'course' + course_id + 'material' + material_id)
    os.makedirs(mat_dir, exist_ok=True)
    for file in files:

        # checking file type
        file_ext = os.path.splitext(file.filename)[1].lower()
        if not file.filename or not file_ext:
            raise HTTPException(status_code=422, detail="File has no name or extension")
        if file_ext not in {'.pdf', '.docx', '.pptx', '.jpg', '.png'}:
            raise HTTPException(status_code=415, detail="Unsupported Media Type")

        # checking file size
        if len(file.content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File is too large")

        # putting file into database and getting fileid
        fileid = repo_mat.sql_insert_material_attachment(db_cursor, course_id, material_id)

        # creating file path
        file_path = os.path.join(mat_dir, fileid) + file_ext

        # saving file
        with open(file_path, "wb") as buffer:
            buffer.write(file.read())

    db_conn.commit()


def remove_material(db_conn, db_cursor, course_id: str, material_id: str, user_email: str):
    # checking constraints
    constraints.assert_material_exists(db_cursor, course_id, material_id)
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # remove material
    repo_mat.sql_delete_material(db_cursor, course_id, material_id)
    db_conn.commit()

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
