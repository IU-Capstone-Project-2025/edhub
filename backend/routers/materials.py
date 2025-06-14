from typing import List
from routers.auth import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException
import models.api
import repository.courses as courses_repo
import repository.users as users_repo
import repository.materials as mats_repo

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

    with get_db() as (db_conn, db_cursor):
        courses_repo.assert_course_exists(db_cursor, course_id)
        users_repo.assert_teacher_access(db_cursor, user_email, course_id)
        material_id = mats_repo.create_material(
            db_cursor, db_conn, course_id, title, description
        )
    return {"course_id": course_id, "material_id": material_id}


@router.post("/remove_material", response_model=models.api.Success)
async def remove_material(
    course_id: str, material_id: str, user_email: str = Depends(get_current_user)
):
    """
    Remove the material by the provided course_id and material_id.

    Teacher role required.
    """

    with get_db() as (db_conn, db_cursor):
        mats_repo.assert_material_exists(db_cursor, course_id, material_id)
        users_repo.assert_teacher_access(db_cursor, user_email, course_id)
        mats_repo.remove_material(db_cursor, db_conn, course_id, material_id)
    return {"success": True}


@router.get("/get_material", response_model=models.api.Material)
async def get_material(
    course_id: str, material_id: str, user_email: str = Depends(get_current_user)
):
    """
    Get the material details by the provided (course_id, material_id).

    Returns course_id, material_id, creation_date, title, and description.
    """

    with get_db() as (db_conn, db_cursor):
        courses_repo.assert_course_exists(db_cursor, course_id)
        courses_repo.assert_course_access(db_cursor, user_email, course_id)
        material = mats_repo.get_material(db_cursor, course_id, material_id)
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
