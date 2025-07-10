from typing import List
from fastapi import APIRouter, Depends
from fastapi import responses

from auth import get_current_user
import json_classes
import logic.courses
import logic.students
import logic.assignments

import database

router = APIRouter()


@router.get("/available_courses", response_model=List[json_classes.CourseId])
async def available_courses(user_email: str = Depends(get_current_user)):
    """
    Get the list of IDs of courses available for user (as a teacher, student, or parent).
    """
    with database.get_system_conn() as db_conn:
        return logic.courses.available_courses(db_conn, user_email)


@router.get("/get_all_courses", response_model=List[json_classes.CourseId])
async def get_all_courses(user_email: str = Depends(get_current_user)):
    """
    Get the list of IDs of all courses in the system.

    Admin role required.
    """
    with database.get_system_conn() as db_conn:
        return logic.courses.get_all_courses(db_conn, user_email)


@router.post("/create_course", response_model=json_classes.CourseId)
async def create_course(title: str, user_email: str = Depends(get_current_user)):
    """
    Create the course with provided title and become a teacher in it.
    """
    with database.get_system_conn() as db_conn:
        return logic.courses.create_course(db_conn, title, user_email)


# WARNING: update if new elements appear
@router.post("/remove_course", response_model=json_classes.Success)
async def remove_course(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Remove the course with provided course_id.

    All the course materials, teachers, students, and parents will be also removed.

    Teacher role required.
    """
    with database.get_system_conn() as db_conn:
        return logic.courses.remove_course(db_conn, course_id, user_email)


@router.get("/get_course_info", response_model=json_classes.Course)
async def get_course_info(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Get information about the course: course_id, title, creation date, and number of enrolled students.
    """
    with database.get_system_conn() as db_conn:
        return logic.courses.get_course_info(db_conn, course_id, user_email)


@router.get("/get_course_feed", response_model=List[json_classes.CoursePost])
async def get_course_feed(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the course feed with all its materials.

    Materials are ordered by creation_date, the first posts are new.

    Returns the list of (course_id, post_id, type, timeadded, author) for each material.
    """
    with database.get_system_conn() as db_conn:
        return logic.courses.get_course_feed(db_conn, course_id, user_email)


@router.get("/download_full_course_grade_table")
async def download_full_course_grade_table(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Download a CSV file (comma-separated, CRLF newlines) with all grades of all students.

    COLUMNS: student login, student display name, then assignment names
    """
    with database.get_system_conn() as db_conn:
        students = [i["email"] for i in logic.students.get_enrolled_students(db_conn, course_id, user_email)]
        gradables = logic.assignments.get_all_assignments(db_conn, course_id, user_email)
        csv_text = logic.courses.get_grade_table_csv(db_conn, course_id, students, gradables, user_email)
        return responses.PlainTextResponse(
            csv_text, media_type="text/csv", headers={"Content-Disposition": "filename=report.csv"}
        )
