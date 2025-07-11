import edhub_errors
from constants import TIME_FORMAT
import constraints
import sql.courses
import sql.teachers
import sql.users
import logic.users
import logic.csvtables
from typing import Union
import itertools


available_courses = sql.courses.select_available_courses


get_all_courses = sql.courses.select_all_courses


def create_course_with_teacher(db_conn, title: str, teacher_email: str) -> str:
    """
    Returns the ID of the new course
    """
    course_id = sql.courses.insert_course(db_conn, title)
    sql.teachers.insert_teacher(db_conn, teacher_email, course_id)
    return course_id


remove_course = sql.courses.delete_course


get_course_info = sql.courses.select_course_info


get_course_feed = sql.courses.select_course_feed


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
    values = sql.courses.select_grades_in_course(db_conn, course_id, students, gradables)
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


def get_grade_table_csv(db_conn, course_id: str, students: list[str], gradables: list[int]) -> str:
    """
    Compile a CSV file (comma-separated, CRLF newlines) with all grades of all students.

    COLUMNS: student login, student display name, then assignment names
    """
    with db_conn.cursor() as db_cursor:
        table = get_grade_table(db_conn, course_id, students, gradables)
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
