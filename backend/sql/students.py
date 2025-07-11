from sql.dto import UserEmailNameDTO


def select_enrolled_students(conn, course_id: str) -> list[UserEmailNameDTO]:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT
                s.email,
                u.publicname
            FROM student_at s
            JOIN users u ON s.email = u.email
            WHERE s.courseid = %s
            """,
            (course_id,),
        )
        return [UserEmailNameDTO(*attrs) for attrs in db_cursor.fetchall()]


def insert_student_at(conn, student_email: str, course_id: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "INSERT INTO student_at (email, courseid) VALUES (%s, %s)",
            (student_email, course_id),
        )


def delete_student_at(conn, course_id: str, student_email: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "DELETE FROM student_at WHERE courseid = %s AND email = %s",
            (course_id, student_email),
        )
