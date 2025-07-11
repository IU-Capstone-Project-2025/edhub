from sql.dto import UserEmailNameDTO


def select_students_parents(conn, course_id: str, student_email: str) -> list[UserEmailNameDTO]:
    """
    Returns a list of pairs `(email, publicName)` of all parents of the given student at the given course
    """
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT
                p.parentemail,
                u.publicname
            FROM parent_of_at_course p
            JOIN users u ON p.parentemail = u.email
            WHERE p.courseid = %s AND p.studentemail = %s
            """,
            (course_id, student_email),
        )
        return [UserEmailNameDTO(*attrs) for attrs in db_cursor.fetchall()]


def insert_parent_of_at_course(conn, parent_email: str, student_email: str, course_id: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "INSERT INTO parent_of_at_course (parentemail, studentemail, courseid) VALUES (%s, %s, %s)",
            (parent_email, student_email, course_id),
        )


def delete_parent_of_at_course(conn, course_id: str, student_email: str, parent_email: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "DELETE FROM parent_of_at_course WHERE courseid = %s AND studentemail = %s AND parentemail = %s",
            (course_id, student_email, parent_email),
        )


def select_parents_children(conn, course_id: str, parent_email: str) -> list[UserEmailNameDTO]:
    """
    Returns a list of pairs `(email, publicName)` of all children of the given parent at the given course
    """
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT
                p.studentemail,
                u.publicname
            FROM parent_of_at_course p
            JOIN users u ON p.studentemail = u.email
            WHERE p.courseid = %s AND p.parentemail = %s
            """,
            (course_id, parent_email),
        )
        return [UserEmailNameDTO(*attrs) for attrs in db_cursor.fetchall()]


def sql_has_child_at_course(conn, course_id: str, parent_email: str, student_email: str) -> bool:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT EXISTS(SELECT 1 FROM parent_of_at_course
            WHERE courseid = %s AND parentemail = %s AND studentemail = %s)
            """,
            (course_id, parent_email, student_email),
        )
        return db_cursor.fetchone()[0]
