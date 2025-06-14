from fastapi import HTTPException
import repository.courses as courses_repo
import repository.users as users_repo


def available_courses_logic(db_cursor, user_email):
    return courses_repo.get_available_courses(db_cursor, user_email)


def create_course_logic(db_cursor, db_conn, title, user_email):
    return courses_repo.create_course_add_teacher(db_cursor, db_conn, title, user_email)


def remove_course_logic(db_cursor, db_conn, course_id, user_email):
    courses_repo.assert_course_exists(db_cursor, course_id)
    users_repo.assert_teacher_access(db_cursor, user_email, course_id)
    courses_repo.remove_course(db_cursor, db_conn, course_id)
    return {"success": True}


def get_course_info_logic(db_cursor, course_id, user_email):
    courses_repo.assert_course_exists(db_cursor, course_id)
    courses_repo.assert_course_access(db_cursor, user_email, course_id)
    course = courses_repo.get_course_info(db_cursor, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return {
        "course_id": str(course[0]),
        "title": course[1],
        "creation_date": course[2].strftime("%m-%d-%Y %H:%M:%S"),
        "number_of_students": course[3],
    }


def get_course_feed_logic(db_cursor, course_id, user_email):
    courses_repo.assert_course_exists(db_cursor, course_id)
    courses_repo.assert_course_access(db_cursor, user_email, course_id)
    course_feed = courses_repo.get_course_feed(db_cursor, course_id)
    return [{"course_id": str(mat[0]), "material_id": mat[1]} for mat in course_feed]
