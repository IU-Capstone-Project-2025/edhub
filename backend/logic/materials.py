from fastapi import HTTPException
from constants import TIME_FORMAT
import constraints
import repo.materials as repo_mat


def create_material(
    db_conn, db_cursor, course_id: str, title: str, description: str, user_email: str
):
    # checking constraints
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # create material
    material_id = repo_mat.sql_insert_material(
        db_cursor, course_id, title, description, user_email
    )
    db_conn.commit()

    return {"course_id": course_id, "material_id": material_id}


def remove_material(
    db_conn, db_cursor, course_id: str, material_id: str, user_email: str
):
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
