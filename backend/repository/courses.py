from fastapi import HTTPException


# checking whether the course exists in our LMS
def assert_course_exists(db_cursor, course_id: str):
    db_cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM courses WHERE courseid = %s)", (course_id,)
    )
    course_exists = db_cursor.fetchone()[0]
    if not course_exists:
        raise HTTPException(status_code=404, detail="No course with provided ID")
    return True


# checking whether the user has general access to the course
def assert_course_access(db_cursor, user_email: str, course_id: str):
    db_cursor.execute(
        """
        SELECT EXISTS(
            SELECT 1 FROM teaches WHERE email = %s AND courseid = %s
            UNION
            SELECT 1 FROM student_at WHERE email = %s AND courseid = %s
            UNION
            SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND courseid = %s
        )
    """,
        (user_email, course_id, user_email, course_id, user_email, course_id),
    )
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        raise HTTPException(
            status_code=403, detail="User does not have access to this course"
        )
    return True


def get_available_courses(db_cursor, user_email):
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
    courses = db_cursor.fetchall()

    return [{"course_id": crs[0]} for crs in courses]


def create_course(db_cursor, db_conn, title):
    db_cursor.execute(
        "INSERT INTO courses (courseid, name, timecreated) VALUES (gen_random_uuid(), %s, now()) RETURNING courseid",
        (title,),
    )
    course_id = db_cursor.fetchone()[0]
    db_conn.commit()

    return course_id


def add_teacher_to_course(db_cursor, db_conn, user_email, course_id):
    db_cursor.execute(
        "INSERT INTO teaches (email, courseid) VALUES (%s, %s)",
        (user_email, course_id),
    )
    db_conn.commit()


# TODO: separate into multiple methods
def create_course_add_teacher(db_cursor, db_conn, title, user_email):
    course_id = create_course(db_cursor, db_conn, title)
    add_teacher_to_course(db_cursor, db_conn, user_email, course_id)

    return course_id


# TODO: separate into multiple methods
def remove_course(db_cursor, db_conn, course_id):
    db_cursor.execute("DELETE FROM course_materials_attachments WHERE courseid = %s", (course_id,))
    db_conn.commit()

    db_cursor.execute("DELETE FROM course_materials WHERE courseid = %s", (course_id,))
    db_conn.commit()

    db_cursor.execute("DELETE FROM parent_of_at_course WHERE courseid = %s", (course_id,))
    db_conn.commit()

    db_cursor.execute("DELETE FROM student_at WHERE courseid = %s", (course_id,))
    db_conn.commit()

    db_cursor.execute("DELETE FROM teaches WHERE courseid = %s", (course_id,))
    db_conn.commit()

    db_cursor.execute("DELETE FROM courses WHERE courseid = %s", (course_id,))
    db_conn.commit()


def get_course_info(db_cursor, course_id):
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


def get_course_feed(db_cursor, course_id):
    db_cursor.execute(
        "SELECT courseid, matid FROM course_materials WHERE courseid = %s",
        (course_id,),
    )
    return db_cursor.fetchall()
