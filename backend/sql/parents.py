def select_students_parents(db_cursor, course_id, student_email):
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
    return db_cursor.fetchall()


def insert_parent_of_at_course(db_cursor, parent_email, student_email, course_id):
    db_cursor.execute(
        "INSERT INTO parent_of_at_course (parentemail, studentemail, courseid) VALUES (%s, %s, %s)",
        (parent_email, student_email, course_id),
    )


def delete_parent_of_at_course(db_cursor, course_id, student_email, parent_email):
    db_cursor.execute(
        "DELETE FROM parent_of_at_course WHERE courseid = %s AND studentemail = %s AND parentemail = %s",
        (course_id, student_email, parent_email),
    )


def select_parents_children(db_cursor, course_id, parent_email):
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
    return db_cursor.fetchall()


def sql_has_child_at_course(db_cursor, course_id: str, parent_email: str, student_email: str) -> bool:
    db_cursor.execute(
        """
        SELECT EXISTS(SELECT 1 FROM parent_of_at_course
        WHERE courseid = %s AND parentemail = %s AND studentemail = %s)
        """,
        (course_id, parent_email, student_email),
    )
    return db_cursor.fetchone()[0]
