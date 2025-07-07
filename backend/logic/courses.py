from fastapi import HTTPException
from constants import TIME_FORMAT
import constraints
import repo.courses as repo_courses
import repo.teachers as repo_teachers
import logic.logging as logger
import logic.users
import repo.parents
from typing import Union


def available_courses(db_cursor, user_email: str):
    courses = repo_courses.sql_select_available_courses(db_cursor, user_email)
    result = [{"course_id": crs[0]} for crs in courses]
    return result


def create_course(db_conn, db_cursor, title: str, user_email: str):
    course_id = repo_courses.sql_insert_course(db_cursor, title)
    repo_teachers.sql_insert_teacher(db_cursor, user_email, course_id)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_COURSE_ADD, f"User {user_email} created course {course_id}")

    return {"course_id": course_id}


def remove_course(db_conn, db_cursor, course_id: str, user_email: str):
    constraints.assert_teacher_access(db_cursor, user_email, course_id)
    repo_courses.sql_delete_course(db_cursor, course_id)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_COURSE_DEL, f"User {user_email} deleted course {course_id}")

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


def get_grade_table_unchecked(db_cursor, course_id: str, students: list[str],
                              gradeables: list[int]) -> list[list[Union[int, None]]]:
    """
    Returns:
    1) the list of row names - student logins;
    2) the list of column names - assignment IDs;
    3) a `len(students) x len(gradeables)` table of grades. Rows and columns are not included.
    Currently, gradeables are just IDs of assignments in this course.
    """
    values = repo_courses.sql_select_grades_in_course(db_cursor, course_id, students, gradeables)
    allrows = sorted(set(v[0] for v in values)) if students is None else students
    allcols = sorted(set(v[1] for v in values)) if gradeables is None else gradeables
    nrows = len(allrows)
    ncols = len(allcols)
    rowindex = {allrows[i]: i for i in range(nrows)}
    colindex = {allcols[i]: i for i in range(ncols)}
    table = [[None] * ncols for _ in range(nrows)]
    for email, assignment, grade in values:
        table[rowindex[email]][colindex[assignment]] = grade
    return table


def get_grade_table(db_cursor, course_id: str, students: list[str],
                    gradeables: list[int], user_email: str) -> list[list[Union[int, None]]]:
    role = logic.users.get_user_role(db_cursor, course_id, user_email)
    if role["is_parent"]:
        children = {i[0] for i in repo.parents.sql_select_parents_children(db_cursor, course_id, user_email)}
        for student in students:
            if student not in children:
                raise HTTPException(


def get_grade_table_csv(db_cursor, course_id: str, students: list[str],
                        gradeables: list[int], user_email: str) -> str:
    """
    Compile a CSV file (comma-separated, CRLF newlines) with all grades of all students.

    ROWS: students' logins

    COLUMNS: student display name, then assignment names
    """
    logic_get_grade_table_csv(db_cursor, course_id, None, None, user_email)

