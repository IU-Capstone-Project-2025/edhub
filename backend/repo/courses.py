from typing import Union


def sql_select_available_courses(db_cursor, user_email):
    db_cursor.execute(
        """
        SELECT courseid AS cid FROM teaches WHERE email = %s
        UNION
        SELECT courseid AS cid FROM student_at WHERE email = %s
        UNION
        SELECT courseid AS cid FROM parent_of_at_course WHERE parentemail = %s
        """,
        (user_email, user_email, user_email),
    )
    return db_cursor.fetchall()


def sql_select_all_courses(db_cursor):
    db_cursor.execute("SELECT courseid FROM courses")
    return db_cursor.fetchall()


def sql_insert_course(db_cursor, title):
    db_cursor.execute(
        "INSERT INTO courses (courseid, name, timecreated) VALUES (gen_random_uuid(), %s, now()) RETURNING courseid",
        (title,),
    )
    return db_cursor.fetchone()[0]


def sql_delete_course(db_cursor, course_id):
    db_cursor.execute("DELETE FROM courses WHERE courseid = %s", (course_id,))


def sql_select_course_info(db_cursor, course_id):
    db_cursor.execute(
        """
        SELECT c.courseid, c.name, c.timecreated, COUNT(sa.email) AS student_count
        FROM courses c
        LEFT JOIN student_at sa ON c.courseid = sa.courseid
        WHERE c.courseid = %s
        GROUP BY c.courseid
        """,
        (course_id,),
    )
    return db_cursor.fetchone()


def sql_select_course_feed(db_cursor, course_id):
    db_cursor.execute(
        """
        SELECT courseid AS cid, matid as postid, 'mat' as type, timeadded, author
        FROM course_materials
        WHERE courseid = %s

        UNION

        SELECT courseid AS cid, assid as postid, 'ass' as type, timeadded, author
        FROM course_assignments
        WHERE courseid = %s

        ORDER BY timeadded DESC
        """,
        (course_id, course_id),
    )
    return db_cursor.fetchall()


def sql_select_grades_in_course(db_cursor, course_id: str,
                                students: Union[list[str], None] = None,
                                assignments: Union[list[int], None] = None) -> list[tuple[str, int, Union[int, None]]]:
    query = "SELECT email, assid, grade FROM course_assignments_submissions WHERE courseid = %s"
    qargs = [course_id]
    if students is not None:
        query += " AND email in %s"
        qargs.append(tuple(students))
    if assignments is not None:
        query += " AND assid in %s"
        qargs.append(tuple(assignments))
    db_cursor.execute(query, tuple(qargs))
    return db_cursor.fetchall()
