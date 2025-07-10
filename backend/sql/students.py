def select_enrolled_students(db_cursor, course_id):
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
    return db_cursor.fetchall()


def insert_student_at(db_cursor, student_email, course_id):
    db_cursor.execute(
        "INSERT INTO student_at (email, courseid) VALUES (%s, %s)",
        (student_email, course_id),
    )


def delete_student_at(db_cursor, course_id, student_email):
    db_cursor.execute(
        "DELETE FROM student_at WHERE courseid = %s AND email = %s",
        (course_id, student_email),
    )
