from fastapi import HTTPException
from constants import TIME_FORMAT
import constraints
import repo.courses
import repo.teachers
import repo.users
import logic.logging as logger
import logic.users
import logic.csvtables
from typing import Union
import itertools


def available_courses(db_cursor, user_email: str):
    courses = repo.courses.sql_select_available_courses(db_cursor, user_email)
    result = [{"course_id": crs[0]} for crs in courses]
    return result


def get_all_courses(db_cursor, user_email: str):
    constraints.assert_admin_access(db_cursor, user_email)
    courses = repo.courses.sql_select_all_courses(db_cursor)
    result = [{"course_id": crs[0]} for crs in courses]
    return result


def create_course(db_conn, db_cursor, title: str, user_email: str):
    course_id = repo.courses.sql_insert_course(db_cursor, title)
    repo.teachers.sql_insert_teacher(db_cursor, user_email, course_id)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_COURSE_ADD, f"User {user_email} created course {course_id}")

    return {"course_id": course_id}


def remove_course(db_conn, db_cursor, course_id: str, user_email: str):
    constraints.assert_teacher_access(db_cursor, user_email, course_id)
    repo.courses.sql_delete_course(db_cursor, course_id)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_COURSE_DEL, f"User {user_email} deleted course {course_id}")

    return {"success": True}


def get_course_info(db_cursor, course_id: str, user_email: str):
    constraints.assert_course_access(db_cursor, user_email, course_id)
    course = repo.courses.sql_select_course_info(db_cursor, course_id)
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
    course_feed = repo.courses.sql_select_course_feed(db_cursor, course_id)
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


def get_all_grades(db_cursor, course_id: str, students: list[str],
                   gradables: list[int], user_email: str) -> list[tuple[str, int, Union[None, int]]]:
    constraints.assert_user_exists(db_cursor, user_email)
    constraints.assert_course_exists(db_cursor, course_id)
    role = logic.users.get_user_role(db_cursor, course_id, user_email)
    if role["is_parent"]:
        constraints.assert_parent_of_all(db_cursor, user_email, students, course_id)
    elif role["is_student"]:
        for student in students:
            if student != user_email:
                raise HTTPException(403, "A student cannot view other students' grades")
    return repo.courses.sql_select_grades_in_course(db_cursor, course_id, students, gradables)


def get_grade_table(db_cursor, course_id: str, students: list[str],
                    gradables: list[int], user_email: str) -> list[list[Union[int, None]]]:
    """
    Returns:
    1) the list of row names - student logins;
    2) the list of column names - assignment IDs;
    3) a `len(students) x len(gradables)` table of grades. Rows and columns are not included.
    Currently, gradables are just IDs of assignments in this course.
    """
    values = get_all_grades(db_cursor, course_id, students, gradables, user_email)
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


def get_grade_table_csv(db_cursor, course_id: str, students: list[str],
                        gradables: list[int], user_email: str) -> str:
    """
    Compile a CSV file (comma-separated, CRLF newlines) with all grades of all students.

    COLUMNS: student login, student display name, then assignment names
    """
    table = get_grade_table(db_cursor, course_id, students, gradables, user_email)
    columns = itertools.chain(("Login", "Public Name",), gradables)
    for login, row in zip(students, table):
        row.insert(0, login)
        row.insert(1, repo.users.sql_get_user_name(db_cursor, login))
    return logic.csvtables.encode_to_csv_with_columns(columns, table)


def get_students_accessible_by(db_cursor, course_id: str, user_email: str) -> list[str]:
    """
    Returns the list of logins of students whose grades are visible by `user_email`.

    In particular, returns an empty list if the user is not associated with the given course.
    """
    role = logic.users.get_user_role(db_cursor, course_id, user_email)
    if role["is_teacher"] or role["is_admin"]:
        return [email for email, name in repo.students.sql_select_enrolled_students(db_cursor, course_id)]
    if role["is_parent"]:
        return [email for email, name in repo.parents.sql_select_parents_children(db_cursor, course_id, user_email)]
    elif role["is_student"]:
        return [user_email]
    else:
        return []
