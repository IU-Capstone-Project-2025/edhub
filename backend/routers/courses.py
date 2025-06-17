from typing import List
from fastapi import APIRouter, Depends

from auth import get_current_user, get_db
from constants import TIME_FORMAT
import json_classes
from logic.courses import (
    available_courses as logic_available_courses,
    create_course as logic_create_course,
    remove_course as logic_remove_course,
    get_course_info as logic_get_course_info,
    get_course_feed as logic_get_course_feed,
)

router = APIRouter()


@router.get("/available_courses", response_model=List[json_classes.CourseId])
async def available_courses(user_email: str = Depends(get_current_user)):
    """
    Get the list of IDs of courses available for user (as a teacher, student, or parent).
    """
    with get_db() as (db_conn, db_cursor):
        return logic_available_courses(db_cursor, user_email)


@router.post("/create_course", response_model=json_classes.CourseId)
async def create_course(title: str, user_email: str = Depends(get_current_user)):
    """
    Create the course with provided title and become a teacher in it.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_create_course(db_conn, db_cursor, title, user_email)


# WARNING: update if new elements appear
@router.post("/remove_course", response_model=json_classes.Success)
async def remove_course(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Remove the course with provided course_id.

    All the course materials, teachers, students, and parents will be also removed.

    Teacher role required.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_remove_course(db_conn, db_cursor, course_id, user_email)


@router.get("/get_course_info", response_model=json_classes.Course)
async def get_course_info(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Get information about the course: course_id, title, creation date, and number of enrolled students.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_get_course_info(db_cursor, course_id, user_email)


@router.get("/get_course_feed", response_model=List[json_classes.CoursePost])
async def get_course_feed(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the course feed with all its materials.

    Materials are ordered by creation_date, the first posts are new.

    Returns the list of (course_id, post_id, type, timeadded, author) for each material.
    """
    with get_db() as (db_conn, db_cursor):
        return logic_get_course_feed(db_cursor, course_id, user_email)
