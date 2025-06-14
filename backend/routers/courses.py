from typing import List
from routers.auth import get_current_user, get_db
from fastapi import APIRouter, Depends
import models.api
import logic.courses as courses_logic

router = APIRouter()


@router.get("/available_courses", response_model=List[models.api.CourseId])
async def available_courses(user_email: str = Depends(get_current_user)):
    with get_db() as (db_conn, db_cursor):
        return courses_logic.available_courses_logic(db_cursor, user_email)


@router.post("/create_course", response_model=models.api.CourseId)
async def create_course(title: str, user_email: str = Depends(get_current_user)):
    with get_db() as (db_conn, db_cursor):
        course_id = courses_logic.create_course_logic(
            db_cursor, db_conn, title, user_email
        )
        return {"course_id": course_id}


@router.post("/remove_course", response_model=models.api.Success)
async def remove_course(course_id: str, user_email: str = Depends(get_current_user)):
    with get_db() as (db_conn, db_cursor):
        return courses_logic.remove_course_logic(
            db_cursor, db_conn, course_id, user_email
        )


@router.get("/get_course_info", response_model=models.api.Course)
async def get_course_info(course_id: str, user_email: str = Depends(get_current_user)):
    with get_db() as (db_conn, db_cursor):
        return courses_logic.get_course_info_logic(db_cursor, course_id, user_email)


@router.get("/get_course_feed", response_model=List[models.api.MaterialID])
async def get_course_feed(course_id: str, user_email: str = Depends(get_current_user)):
    with get_db() as (db_conn, db_cursor):
        return courses_logic.get_course_feed_logic(db_cursor, course_id, user_email)
