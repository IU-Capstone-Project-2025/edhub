def sql_select_course_teachers(db_cursor, course_id):
    db_cursor.execute(
        """
        SELECT
            t.email,
            u.publicname
        FROM teaches t
        JOIN users u ON t.email = u.email
        WHERE t.courseid = %s
        GROUP BY t.email, u.publicname
        """,
        (course_id,),
    )
    return db_cursor.fetchall()


def sql_insert_teacher(db_cursor, new_teacher_email, course_id):
    db_cursor.execute(
        "INSERT INTO teaches (email, courseid) VALUES (%s, %s)",
        (new_teacher_email, course_id),
    )


def sql_count_teachers(db_cursor, course_id):
    db_cursor.execute("SELECT COUNT(*) FROM teaches WHERE courseid = %s", (course_id,))
    return db_cursor.fetchone()[0]


def sql_delete_teacher(db_cursor, course_id, removing_teacher_email):
    db_cursor.execute(
        "DELETE FROM teaches WHERE courseid = %s AND email = %s",
        (course_id, removing_teacher_email),
    )
