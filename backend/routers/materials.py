from typing import List
from routers.auth import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException
import models.api, constraints
from routers.auth import get_current_user, get_db

router = APIRouter()


@router.post("/create_material", response_model=models.api.MaterialID)
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

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_exists(db_cursor, course_id)
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        # create material
        db_cursor.execute(
            "INSERT INTO course_materials (courseid, name, description, timeadded) VALUES (%s, %s, %s, now()) RETURNING matid",
            (course_id, title, description),
        )
        material_id = db_cursor.fetchone()[0]
        db_conn.commit()

    return {"course_id": course_id, "material_id": material_id}


@router.post("/remove_material", response_model=models.api.Success)
async def remove_material(
    course_id: str, material_id: str, user_email: str = Depends(get_current_user)
):
    """
    Remove the material by the provided course_id and material_id.

    Teacher role required.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

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


@router.get("/get_material", response_model=models.api.Material)
async def get_material(
    course_id: str, material_id: str, user_email: str = Depends(get_current_user)
):
    """
    Get the material details by the provided (course_id, material_id).

    Returns course_id, material_id, creation_date, title, and description.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_exists(db_cursor, course_id)
        constraints.assert_course_access(db_cursor, user_email, course_id)

        # searching for materials
        db_cursor.execute(
            """
            SELECT courseid, matid, timeadded, name, description
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
        "creation_date": material[2].strftime("%m-%d-%Y %H:%M:%S"),
        "title": material[3],
        "description": material[4],
    }
    return res
