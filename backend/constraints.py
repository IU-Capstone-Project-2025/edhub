from fastapi import HTTPException

# checking whether the user exists in our LMS
def assert_user_exists(db_cursor, user_email: str):
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (user_email,))
    user_exists = db_cursor.fetchone()[0]
    if not user_exists:
        raise HTTPException(status_code=404, detail="No user with provided email")


# checking whether the course exists in our LMS
def assert_course_exists(db_cursor, course_id: str):
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM courses WHERE courseid = %s)", (course_id,))
    course_exists = db_cursor.fetchone()[0]
    if not course_exists:
        raise HTTPException(status_code=404, detail="No course with provided ID")


# checking whether the course exists in our LMS
def assert_material_exists(db_cursor, course_id: str, material_id: str):
    try:
        material_id = int(material_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Material ID should be integer")

    assert_course_exists(db_cursor, course_id)
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM course_materials WHERE courseid = %s AND matid = %s  )", (course_id, material_id))
    material_exists = db_cursor.fetchone()[0]
    if not material_exists:
        raise HTTPException(status_code=404, detail="No material with provided ID in this course")

# checking whether the assignment exists in our LMS
def assert_assignment_exists(db_cursor, course_id: str, assignment_id: str):
    try:
        assignment_id = int(assignment_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Assignment ID should be integer")

    assert_course_exists(db_cursor, course_id)
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM course_assignments WHERE courseid = %s AND assid = %s)", (course_id, assignment_id))
    assignment_exists = db_cursor.fetchone()[0]
    if not assignment_exists:
        raise HTTPException(status_code=404, detail="No assignment with provided ID in this course")

# checking whether the student's submission exists in our LMS
def assert_submission_exists(db_cursor, course_id: str, assignment_id: str, student_email: str):
    assert_assignment_exists(db_cursor, course_id)
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM course_assignments_submissions WHERE courseid = %s AND assid = %s AND email = %s)", (course_id, assignment_id, student_email))
    submission_exists = db_cursor.fetchone()[0]
    if not submission_exists:
        raise HTTPException(status_code=404, detail="Submission of this user is not found")


# checking whether the user has general access to the course
def assert_course_access(db_cursor, user_email: str, course_id: str):
    db_cursor.execute("""
        SELECT EXISTS(
            SELECT 1 FROM teaches WHERE email = %s AND courseid = %s
            UNION
            SELECT 1 FROM student_at WHERE email = %s AND courseid = %s
            UNION
            SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND courseid = %s
        )
    """, (user_email, course_id, user_email, course_id, user_email, course_id))
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        raise HTTPException(status_code=403, detail="User does not have access to this course")


# checking whether the user has teacher access to the course
def check_teacher_access(db_cursor, teacher_email: str, course_id: str):
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM teaches WHERE email = %s AND courseid = %s)", (teacher_email, course_id))
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        return False
    return True


def assert_teacher_access(db_cursor, teacher_email: str, course_id: str):
    if not check_teacher_access(db_cursor, teacher_email, course_id):
        raise HTTPException(status_code=403, detail="User has not teacher rights at this course")


# checking whether the user has student access to the course
def check_student_access(db_cursor, student_email: str, course_id: str):
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM student_at WHERE email = %s AND courseid = %s)", (student_email, course_id))
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        return False
    return True


def assert_student_access(db_cursor, student_email: str, course_id: str):
    if not check_student_access(db_cursor, student_email, course_id):
        raise HTTPException(status_code=403, detail="User has not student rights at this course")


# checking whether the user has parent access to the course
def check_parent_access(db_cursor, parent_email: str, course_id: str):
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND courseid = %s)", (parent_email, course_id))
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        return False
    return True


# checking whether the user has parent access with the student at the course
def check_parent_student_access(db_cursor, parent_email: str, student_email: str, course_id: str):
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND studentemail = %s AND courseid = %s)", (parent_email, student_email, course_id))
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        return False
    return True