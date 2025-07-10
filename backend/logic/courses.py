from fastapi import HTTPException
from constants import TIME_FORMAT
import constraints
import sql.courses
import sql.teachers
import sql.users
import logic.logging as logger
import logic.users
import logic.csvtables
from typing import Union
import itertools


def available_courses(db_conn, user_email: str):
    with db_conn.cursor() as db_cursor:
        courses = sql.courses.select_available_courses(db_cursor, user_email)
        result = [{"course_id": crs[0]} for crs in courses]
        return result


def get_all_courses(db_conn, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_admin_access(db_cursor, user_email)
        courses = sql.courses.select_all_courses(db_cursor)
        result = [{"course_id": crs[0]} for crs in courses]
        return result


def create_course(db_conn, title: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        course_id = sql.courses.insert_course(db_cursor, title)
        sql.teachers.insert_teacher(db_cursor, user_email, course_id)
        db_conn.commit()

        logger.log(db_conn, logger.TAG_COURSE_ADD, f"User {user_email} created course {course_id}")

        return {"course_id": course_id}


def remove_course(db_conn, course_id: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_teacher_access(db_cursor, user_email, course_id)
        sql.courses.delete_course(db_cursor, course_id)
        db_conn.commit()

        logger.log(db_conn, logger.TAG_COURSE_DEL, f"User {user_email} deleted course {course_id}")

        return {"success": True}


def get_course_info(db_conn, course_id: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_course_access(db_cursor, user_email, course_id)
        course = sql.courses.select_course_info(db_cursor, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        res = {
            "course_id": str(course[0]),
            "title": course[1],
            "creation_time": course[2].strftime(TIME_FORMAT),
            "number_of_students": course[3],
        }
        return res


def get_course_feed(db_conn, course_id: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_course_access(db_cursor, user_email, course_id)
        course_feed = sql.courses.select_course_feed(db_cursor, course_id)
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


def get_all_grades(
    db_conn, course_id: str, students: list[str], gradables: list[int], user_email: str
) -> list[tuple[str, int, Union[None, int]]]:
    with db_conn.cursor() as db_cursor:
        constraints.assert_user_exists(db_cursor, user_email)
        constraints.assert_course_exists(db_cursor, course_id)
        role = logic.users.get_user_role(db_cursor, course_id, user_email)
        if role["is_parent"]:
            constraints.assert_parent_of_all(db_cursor, user_email, students, course_id)
        elif role["is_student"]:
            for student in students:
                if student != user_email:
                    raise HTTPException(403, "A student cannot view other students' grades")
        return sql.courses.select_grades_in_course(db_cursor, course_id, students, gradables)


def get_grade_table(
    db_conn, course_id: str, students: list[str], gradables: list[int], user_email: str
) -> list[list[Union[int, None]]]:
    """
    Returns:
    1) the list of row names - student logins;
    2) the list of column names - assignment IDs;
    3) a `len(students) x len(gradables)` table of grades. Rows and columns are not included.
    Currently, gradables are just IDs of assignments in this course.
    """
    values = get_all_grades(db_conn, course_id, students, gradables, user_email)
    allrows = sorted(set(v[0] for v in values)) if students is None else students
    allcols = sorted(set(v[1] for v in values)) if gradables is None else gradables
    nrows = len(allrows)
    ncols = len(allcols)
    rowindex = {allrows[i]: i for i in range(nrows)}
    colindex = {allcols[i]: i for i in range(ncols)}
    table = [[None] * ncols for _ in range(nrows)]
    for email, assignment, grade in values:
        table[rowindex[email]][colindex[assignment]] = grade
    return table


def get_grade_table_csv(db_conn, course_id: str, students: list[str], gradables: list[int], user_email: str) -> str:
    """
    Compile a CSV file (comma-separated, CRLF newlines) with all grades of all students.

    COLUMNS: student login, student display name, then assignment names
    """
    with db_conn.cursor() as db_cursor:
        table = get_grade_table(db_conn, course_id, students, gradables, user_email)
        columns = itertools.chain(
            (
                "Login",
                "Public Name",
            ),
            gradables,
        )
        for login, row in zip(students, table):
            row.insert(0, login)
            row.insert(1, sql.users.get_user_name(db_cursor, login))
        return logic.csvtables.encode_to_csv_with_columns(columns, table)
