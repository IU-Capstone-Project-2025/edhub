from typing import List
from routers.auth import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException
import models.api
from routers.auth import get_current_user, get_db
import repository.courses as courses_repo
import repository.users as users_repo

router = APIRouter()


@router.get("/available_courses", response_model=List[models.api.CourseId])
async def available_courses(user_email: str = Depends(get_current_user)):
    """
    Get the list of IDs of courses available for user (as a teacher, student, or parent).
    """

    # finding available courses
    with get_db() as (db_conn, db_cursor):
        res = courses_repo.get_available_courses(db_cursor, user_email)
        return res


@router.post("/create_course", response_model=models.api.CourseId)
async def create_course(title: str, user_email: str = Depends(get_current_user)):
    """
    Create the course with provided title and become a teacher in it.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):
        course_id = courses_repo.create_course_add_teacher(db_cursor, db_conn, title, user_email)
        return {"course_id": course_id}


@router.post("/remove_course", response_model=models.api.Success)
async def remove_course(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Remove the course with provided course_id.

    All the course materials, teachers, students, and parents will be also removed.

    Teacher role required.
    """

    with get_db() as (db_conn, db_cursor):
        courses_repo.assert_course_exists(db_cursor, course_id)
        users_repo.assert_teacher_access(db_cursor, user_email, course_id)

    # connection to database
    with get_db() as (db_conn, db_cursor):
        courses_repo.remove_course(db_cursor, db_conn, course_id)

    return {"success": True}


@router.get("/get_course_info", response_model=models.api.Course)
async def get_course_info(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Get information about the course: course_id, title, creation date, and number of enrolled students.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        courses_repo.assert_course_exists(db_cursor, course_id)
        courses_repo.assert_course_access(db_cursor, user_email, course_id)

        # getting course info
        get_course_info(db_cursor, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

    res = {
        "course_id": str(course[0]),
        "title": course[1],
        "creation_date": course[2].strftime("%m-%d-%Y %H:%M:%S"),
        "number_of_students": course[3],
    }
    return res


@router.get("/get_course_feed", response_model=List[models.api.MaterialID])
async def get_course_feed(course_id: str, user_email: str = Depends(get_current_user)):
    """
    Get the course feed with all its materials.

    Returns the list of (course_id, material_id) for each material.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        courses_repo.assert_course_exists(db_cursor, course_id)
        courses_repo.assert_course_access(db_cursor, user_email, course_id)

        # finding course feed
        db_cursor.execute(
            "SELECT courseid, matid FROM course_materials WHERE courseid = %s",
            (course_id,),
        )
        course_feed = db_cursor.fetchall()

    res = [{"course_id": str(mat[0]), "material_id": mat[1]} for mat in course_feed]
    return res
