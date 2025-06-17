from fastapi import HTTPException
from constants import TIME_FORMAT
import constraints

# Assuming json_classes contains Pydantic models or similar structures for type hinting if needed,
# but they are not directly used in the logic functions' signatures after removing FastAPI decorators.


def create_material(
    db_conn, db_cursor, course_id: str, title: str, description: str, user_email: str
):

    # checking constraints
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # create material
    db_cursor.execute(
        "INSERT INTO course_materials (courseid, name, description, timeadded, author) VALUES (%s, %s, %s, now(), %s) RETURNING matid",
        (course_id, title, description, user_email),
    )
    material_id = db_cursor.fetchone()[0]
    db_conn.commit()

    return {"course_id": course_id, "material_id": material_id}


def remove_material(
    db_conn, db_cursor, course_id: str, material_id: str, user_email: str
):

    # checking constraints
    constraints.assert_material_exists(db_cursor, course_id, material_id)
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # remove material
    db_cursor.execute(
        "DELETE FROM course_materials WHERE courseid = %s AND matid = %s",
        (course_id, material_id),
    )
    db_conn.commit()

    return {"success": True}


def get_material(db_cursor, course_id: str, material_id: str, user_email: str):

    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # searching for materials
    db_cursor.execute(
        """
        SELECT courseid, matid, timeadded, name, description, author
        FROM course_materials
        WHERE courseid = %s AND matid = %s
    """,
        (course_id, material_id),
    )
    material = db_cursor.fetchone()
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
