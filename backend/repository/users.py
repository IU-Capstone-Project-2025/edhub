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
