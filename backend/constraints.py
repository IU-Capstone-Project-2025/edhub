from fastapi import HTTPException
from typing import Union
#
# value_assert_ functions all return None if no problems were found and the
# check is successful, or an HTTPException if the arguments were invalid or
# if the check failed.
#
# assert_ functions raise an HTTPException if the arguments were invalid or
# if the check failed. They always return None.
#
# check_ functions return True if no problems were found and the
# check is successful, or False if the arguments were invalid or
# if the check failed.
#


# checking whether the user exists in our LMS
def value_assert_user_exists(db_cursor, user_email: str) -> Union[None, HTTPException]:
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (user_email,))
    user_exists = db_cursor.fetchone()[0]
    if not user_exists:
        raise HTTPException(status_code=404, detail="No user with provided email")
    return None


# checking whether the user exists in our LMS
def assert_user_exists(db_cursor, user_email: str):
    err = value_assert_user_exists(db_cursor, user_email)
    if err is not None:
        raise err


# checking whether the user exists in our LMS
def check_user_exists(db_cursor, user_email: str) -> bool:
    return value_assert_user_exists(db_cursor, user_email) is None


# checking whether the course exists in our LMS
def value_assert_course_exists(db_cursor, course_id: str) -> Union[None, HTTPException]:
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM courses WHERE courseid = %s)", (course_id,))
    course_exists = db_cursor.fetchone()[0]
    if not course_exists:
        raise HTTPException(status_code=404, detail="No course with provided ID")
    return None


# checking whether the course exists in our LMS
def assert_course_exists(db_cursor, course_id: str):
    err = value_assert_course_exists(db_cursor, course_id)
    if err is not None:
        raise err


# checking whether the course exists in our LMS
def check_course_exists(db_cursor, course_id: str) -> bool:
    return value_assert_user_exists(db_cursor, course_id) is None


# checking whether the material exists in the course
def value_assert_material_exists(db_cursor, course_id: str, material_id: str) -> Union[None, HTTPException]:
    try:
        material_id = int(material_id)
    except Exception:
        return HTTPException(status_code=400, detail="Material ID should be integer")

    course_exists_error = value_assert_course_exists(db_cursor, course_id)
    if course_exists_error is not None:
        return course_exists_error
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM course_materials WHERE courseid = %s AND matid = %s)", (course_id, material_id))
    material_exists = db_cursor.fetchone()[0]
    if not material_exists:
        return HTTPException(status_code=404, detail="No material with provided ID in this course")
    return None


# checking whether the material exists in the course
def assert_material_exists(db_cursor, course_id: str, material_id: str):
    err = value_assert_material_exists(db_cursor, course_id, material_id)
    if err is not None:
        raise err


# checking whether the material exists in the course
def check_material_exists(db_cursor, course_id: str, material_id: str) -> bool:
    return value_assert_user_exists(db_cursor, course_id, material_id) is None


# checking whether the user has general access to the course,
def value_assert_course_access(db_cursor, user_email: str, course_id: str) -> Union[None, HTTPException]:
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
        return HTTPException(status_code=403, detail="User does not have access to this course")
    return None


# checking whether the user has general access to the course,
def assert_course_access(db_cursor, user_email: str, course_id: str):
    err = value_assert_course_exists(db_cursor, user_email, course_id)
    if err is not None:
        raise err


# checking whether the user has general access to the course,
def check_course_access(db_cursor, user_email: str, course_id: str) -> bool:
    return value_assert_course_exists(db_cursor, user_email, course_id) is None


# checking whether the user has teacher access to the course
def value_assert_teacher_access(db_cursor, teacher_email: str, course_id: str) -> Union[None, HTTPException]:
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM teaches WHERE email = %s AND courseid = %s)", (teacher_email, course_id))
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        return HTTPException(status_code=403, detail="User has no teacher rights in this course")
    return None


# checking whether the user has teacher access to the course
def assert_teacher_access(db_cursor, teacher_email: str, course_id: str):
    err = value_assert_teacher_access(db_cursor, teacher_email, course_id)
    if err is not None:
        raise err


# checking whether the user has teacher access to the course
def check_teacher_access(db_cursor, teacher_email: str, course_id: str) -> bool:
    return value_assert_teacher_access(db_cursor, teacher_email, course_id) is None


# checking whether the user has student access to the course
def value_assert_student_access(db_cursor, student_email: str, course_id: str) -> Union[None, HTTPException]:
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM student_at WHERE email = %s AND courseid = %s)", (student_email, course_id))
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        return HTTPException(status_code=403, detail="User has no student rights in this course")
    return None


# checking whether the user has student access to the course
def assert_student_access(db_cursor, student_email: str, course_id: str):
    err = value_assert_student_access(db_cursor, student_email, course_id)
    if err is not None:
        raise err


# checking whether the user has student access to the course
def check_student_access(db_cursor, student_email: str, course_id: str) -> bool:
    return value_assert_course_exists(db_cursor, student_email, course_id) is None


# checking whether the user has parent access to the course
def value_assert_parent_access(db_cursor, parent_email: str, course_id: str) -> Union[None, HTTPException]:
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND courseid = %s)", (parent_email, course_id))
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        return HTTPException(status_code=403, detail="User has no parental access in this course")
    return None


# checking whether the user has parent access to the course
def assert_parent_access(db_cursor, parent_email: str, course_id: str):
    err = value_assert_parent_access(db_cursor, parent_email, course_id)
    if err is not None:
        raise err


# checking whether the user has parent access to the course
def check_parent_access(db_cursor, parent_email: str, course_id: str) -> bool:
    return value_assert_parent_access(db_cursor, parent_email, course_id) is None


# checking whether the user has parent access with the student in the course
def value_assert_parent_student_access(db_cursor, parent_email: str, student_email: str, course_id: str) -> Union[None, HTTPException]:
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND studentemail = %s AND courseid = %s)", (parent_email, student_email, course_id))
    has_access = db_cursor.fetchone()[0]
    if not has_access:
        return HTTPException(status_code=403, detail="User has no parental access to this student's course")
    return None


# checking whether the user has parent access with the student in the course
def assert_parent_student_access(db_cursor, parent_email: str, student_email: str, course_id: str):
    err = value_assert_parent_student_access(db_cursor, parent_email, student_email, course_id)
    if err is not None:
        raise err


# checking whether the user has parent access with the student in the course
def check_parent_student_access(db_cursor, parent_email: str, student_email: str, course_id: str) -> bool:
    return value_assert_parent_student_access(db_cursor, parent_email, student_email, course_id) is None
