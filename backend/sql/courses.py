def select_available_courses(db_cursor, user_email):
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


def select_all_courses(db_cursor):
    db_cursor.execute("SELECT courseid FROM courses")
    return db_cursor.fetchall()


def insert_course(db_cursor, title):
    db_cursor.execute(
        "INSERT INTO courses (courseid, name, timecreated) VALUES (gen_random_uuid(), %s, now()) RETURNING courseid",
        (title,),
    )
    return db_cursor.fetchone()[0]


def delete_course(db_cursor, course_id):
    db_cursor.execute("DELETE FROM courses WHERE courseid = %s", (course_id,))


def select_course_info(db_cursor, course_id):
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


def select_course_feed(db_cursor, course_id):
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
