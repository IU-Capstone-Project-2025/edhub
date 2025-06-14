from fastapi import HTTPException


def assert_user_exists(db_cursor, user_email: str):
    db_cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (user_email,)
    )
    user_exists = db_cursor.fetchone()[0]
    if not user_exists:
        raise HTTPException(status_code=404, detail="No user with provided email")
    return True


# checking whether the user has teacher access to the course
def check_teacher_access(db_cursor, teacher_email: str, course_id: str):
    db_cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM teaches WHERE email = %s AND courseid = %s)",
        (teacher_email, course_id),
    )
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        return False
    return True


def assert_teacher_access(db_cursor, teacher_email: str, course_id: str):
    if not check_teacher_access(db_cursor, teacher_email, course_id):
        raise HTTPException(
            status_code=403, detail="User has not teacher rights at this course"
        )


# checking whether the user has student access to the course
def check_student_access(db_cursor, student_email: str, course_id: str):
    db_cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM student_at WHERE email = %s AND courseid = %s)",
        (student_email, course_id),
    )
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        return False
    return True


def assert_student_access(db_cursor, student_email: str, course_id: str):
    if not check_student_access(db_cursor, student_email, course_id):
        raise HTTPException(
            status_code=403, detail="User has not student rights at this course"
        )


# checking whether the user has parent access to the course
def check_parent_access(db_cursor, parent_email: str, course_id: str):
    db_cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND courseid = %s)",
        (parent_email, course_id),
    )
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        return False
    return True


# checking whether the user has parent access with the student at the course
def check_parent_student_access(
    db_cursor, parent_email: str, student_email: str, course_id: str
):
    db_cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND studentemail = %s AND courseid = %s)",
        (parent_email, student_email, course_id),
    )
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        return False
    return True


def get_enrolled_students(db_conn, course_id):
    cur = db_conn.cursor()
    cur.execute(
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
    students = cur.fetchall()
    res = [{"email": st[0], "name": st[1]} for st in students]
    return res


def add_student_to_course(db_cursor, db_conn, student_email, course_id):
    db_cursor.execute(
        "INSERT INTO student_at (email, courseid) VALUES (%s, %s)",
        (student_email, course_id),
    )
    db_conn.commit()


def remove_student_from_course(db_cursor, db_conn, student_email, course_id):
    db_cursor.execute(
        "DELETE FROM student_at WHERE courseid = %s AND email = %s",
        (course_id, student_email),
    )
    db_conn.commit()


def remove_student_parents(db_cursor, db_conn, student_email, course_id):
    db_cursor.execute(
        "DELETE FROM parent_of_at_course WHERE courseid = %s AND studentemail = %s",
        (course_id, student_email),
    )
    db_conn.commit()


def add_parent_to_student(db_cursor, db_conn, parent_email, student_email, course_id):
    db_cursor.execute(
        "INSERT INTO parent_of_at_course (parentemail, studentemail, courseid) VALUES (%s, %s, %s)",
        (parent_email, student_email, course_id),
    )
    db_conn.commit()


def remove_parent_from_student(
    db_cursor, db_conn, parent_email, student_email, course_id
):
    db_cursor.execute(
        "DELETE FROM parent_of_at_course WHERE courseid = %s AND studentemail = %s AND parentemail = %s",
        (course_id, student_email, parent_email),
    )
    db_conn.commit()


def add_teacher_to_course(db_cursor, db_conn, teacher_email, course_id):
    db_cursor.execute(
        "INSERT INTO teaches (email, courseid) VALUES (%s, %s)",
        (teacher_email, course_id),
    )
    db_conn.commit()


def remove_teacher_from_course(db_cursor, db_conn, teacher_email, course_id):
    db_cursor.execute(
        "DELETE FROM teaches WHERE courseid = %s AND email = %s",
        (course_id, teacher_email),
    )
    db_conn.commit()


def count_teachers_in_course(db_cursor, course_id):
    db_cursor.execute("SELECT COUNT(*) FROM teaches WHERE courseid = %s", (course_id,))
    return db_cursor.fetchone()[0]


def get_students_parents(db_cursor, course_id, student_email):
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


def get_course_teachers(db_cursor, course_id):
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


def user_exists(db_cursor, email):
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (email,))
    return db_cursor.fetchone()[0]


def create_user(db_cursor, db_conn, email, name, hashed_password):
    db_cursor.execute(
        "INSERT INTO users (email, publicname, isadmin, timeregistered, passwordhash) VALUES (%s, %s, %s, now(), %s)",
        (email, name, False, hashed_password),
    )
    db_conn.commit()


def get_password_hash(db_cursor, email):
    db_cursor.execute("SELECT passwordhash FROM users WHERE email = %s", (email,))
    result = db_cursor.fetchone()
    return result[0] if result else None
