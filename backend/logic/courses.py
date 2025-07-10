from fastapi import HTTPException
from constants import TIME_FORMAT
import constraints
import sql.courses as sql_courses
import sql.teachers as sql_teachers
import logic.logging as logger


def available_courses(db_cursor, user_email: str):
    courses = sql_courses.select_available_courses(db_cursor, user_email)
    result = [{"course_id": crs[0]} for crs in courses]
    return result


def get_all_courses(db_cursor, user_email: str):
    constraints.assert_admin_access(db_cursor, user_email)
    courses = sql_courses.select_all_courses(db_cursor)
    result = [{"course_id": crs[0]} for crs in courses]
    return result


def create_course(db_conn, db_cursor, title: str, user_email: str):
    course_id = sql_courses.insert_course(db_cursor, title)
    sql_teachers.insert_teacher(db_cursor, user_email, course_id)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_COURSE_ADD, f"User {user_email} created course {course_id}")

    return {"course_id": course_id}


def remove_course(db_conn, db_cursor, course_id: str, user_email: str):
    constraints.assert_teacher_access(db_cursor, user_email, course_id)
    sql_courses.delete_course(db_cursor, course_id)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_COURSE_DEL, f"User {user_email} deleted course {course_id}")

    return {"success": True}


def get_course_info(db_cursor, course_id: str, user_email: str):
    constraints.assert_course_access(db_cursor, user_email, course_id)
    course = sql_courses.select_course_info(db_cursor, course_id)
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
    course_feed = sql_courses.select_course_feed(db_cursor, course_id)
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
