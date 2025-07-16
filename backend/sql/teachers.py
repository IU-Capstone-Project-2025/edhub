from sql.dto import UserEmailNameDTO


def select_course_teachers(conn, course_id: str) -> list[UserEmailNameDTO]:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT t.email, u.publicname
            FROM teaches t
            JOIN users u ON t.email = u.email
            WHERE t.courseid = %s
            """,
            (course_id,),
        )
        return [UserEmailNameDTO(*attrs) for attrs in db_cursor.fetchall()]


def insert_teacher(conn, new_teacher_email: str, course_id: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "INSERT INTO teaches (email, courseid) VALUES (%s, %s)",
            (new_teacher_email, course_id),
        )


def count_teachers(conn, course_id: str) -> int:
    with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT COUNT(*) FROM teaches WHERE courseid = %s", (course_id,))
        return db_cursor.fetchone()[0]


def delete_teacher(conn, course_id: str, removing_teacher_email: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "DELETE FROM teaches WHERE courseid = %s AND email = %s",
            (course_id, removing_teacher_email),
        )
