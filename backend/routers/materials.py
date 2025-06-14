from typing import List
from routers.auth import get_current_user, get_db
from fastapi import APIRouter, Depends
import models.api
import logic.materials as materials_logic

router = APIRouter()


@router.post("/create_material", response_model=models.api.MaterialID)
async def create_material(
    course_id: str,
    title: str,
    description: str,
    user_email: str = Depends(get_current_user),
):
    with get_db() as (db_conn, db_cursor):
        return materials_logic.create_material_logic(
            db_cursor, db_conn, course_id, title, description, user_email
        )


@router.post("/remove_material", response_model=models.api.Success)
async def remove_material(
    course_id: str, material_id: str, user_email: str = Depends(get_current_user)
):
    with get_db() as (db_conn, db_cursor):
        return materials_logic.remove_material_logic(
            db_cursor, db_conn, course_id, material_id, user_email
        )


@router.get("/get_material", response_model=models.api.Material)
async def get_material(
    course_id: str, material_id: str, user_email: str = Depends(get_current_user)
):
    with get_db() as (db_conn, db_cursor):
        return materials_logic.get_material_logic(
            db_cursor, course_id, material_id, user_email
        )
