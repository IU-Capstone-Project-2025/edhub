from fastapi import HTTPException
from constants import TIME_FORMAT
import constraints
import repo.courses as repo_courses
import repo.teachers as repo_teachers


def available_courses(db_cursor, user_email: str):
    courses = repo_courses.sql_select_available_courses(db_cursor, user_email)
    result = [{"course_id": crs[0]} for crs in courses]
    return result


def create_course(db_conn, db_cursor, title: str, user_email: str):
    course_id = repo_courses.sql_insert_course(db_cursor, title)
    repo_teachers.sql_insert_teacher(db_cursor, user_email, course_id)
    db_conn.commit()
    return {"course_id": course_id}


def remove_course(db_conn, db_cursor, course_id: str, user_email: str):
    constraints.assert_teacher_access(db_cursor, user_email, course_id)
    repo_courses.sql_delete_course(db_cursor, course_id)
    db_conn.commit()
    return {"success": True}


def get_course_info(db_cursor, course_id: str, user_email: str):
    constraints.assert_course_access(db_cursor, user_email, course_id)
    course = repo_courses.sql_select_course_info(db_cursor, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    res = {
        "course_id": str(course[0]),
        "title": course[1],
        "creation_time": course[2].strftime(TIME_FORMAT),
        "number_of_students": course[3],
    }
    return res


def get_course_feed(db_cursor, course_id: str, user_email: str):
    constraints.assert_course_access(db_cursor, user_email, course_id)
    course_feed = repo_courses.sql_select_course_feed(db_cursor, course_id)
    res = [
        {
            "course_id": str(mat[0]),
            "post_id": mat[1],
            "type": mat[2],
            "timeadded": mat[3].strftime(TIME_FORMAT),
            "author": mat[4],
        }
        for mat in course_feed
    ]
    return res
