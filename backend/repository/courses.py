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
