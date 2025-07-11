from typing import Union
import sql.parents
import edhub_errors
from edhub_errors import EdHubException

#
# value_assert_ functions all return None if no problems were found and the
# check is successful, or an EdHubException if the arguments were invalid or
# if the check failed.
#
# assert_ functions raise an EdHubException if the arguments were invalid or
# if the check failed. They always return None.
#
# check_ functions return True if no problems were found and the
# check is successful, or False if the arguments were invalid or
# if the check failed.
#


def value_assert_user_exists(conn, user_email: str) -> Union[None, EdHubException]:
    if not sql.users.select_user_exists(conn, user_email):
        return edhub_errors.UserNotFoundException(user_email)
    return None


def assert_user_exists(conn, user_email: str):
    err = value_assert_user_exists(conn, user_email)
    if err is not None:
        raise err


def check_user_exists(conn, user_email: str) -> bool:
    return value_assert_user_exists(conn, user_email) is None


def value_assert_user_not_exists(conn, user_email: str) -> Union[None, EdHubException]:
    if sql.users.select_user_exists(conn, user_email):
        return edhub_errors.UserExistsException(user_email)
    return None


def assert_user_not_exists(conn, user_email: str):
    err = value_assert_user_not_exists(conn, user_email)
    if err is not None:
        raise err


def value_assert_course_exists(conn, course_id: str) -> Union[None, EdHubException]:
    with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM courses WHERE courseid = %s)", (course_id,))
        course_exists = db_cursor.fetchone()[0]
        if not course_exists:
            return edhub_errors.CourseNotFoundException(course_id)
        return None


def assert_course_exists(conn, course_id: str):
    err = value_assert_course_exists(conn, course_id)
    if err is not None:
        raise err


def check_course_exists(conn, course_id: str) -> bool:
    return value_assert_course_exists(conn, course_id) is None


def value_assert_material_exists(conn, course_id: str, material_id: str) -> Union[None, EdHubException]:
    try:
        material_id = int(material_id)
    except ValueError:
        return edhub_errors.ParameterNotIntegerException("material_id", material_id)

    err = value_assert_course_exists(conn, course_id)
    if err is not None:
        return err
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM course_materials WHERE courseid = %s AND matid = %s)", (course_id, material_id)
        )
        material_exists = db_cursor.fetchone()[0]
    if not material_exists:
        return edhub_errors.MaterialNotFoundException(course_id, material_id)
    return None


def assert_material_exists(conn, course_id: str, material_id: str):
    err = value_assert_material_exists(conn, course_id, material_id)
    if err is not None:
        raise err


def check_material_exists(conn, course_id: str, material_id: str) -> bool:
    return value_assert_material_exists(conn, course_id, material_id) is None


def value_assert_assignment_exists(conn, course_id: str, assignment_id: str) -> Union[None, EdHubException]:
    try:
        assignment_id = int(assignment_id)
    except ValueError:
        return edhub_errors.ParameterNotIntegerException("assignment_id", assignment_id)

    err = value_assert_course_exists(conn, course_id)
    if err is not None:
        return err
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM course_assignments WHERE courseid = %s AND assid = %s)",
            (course_id, assignment_id),
        )
        assignment_exists = db_cursor.fetchone()[0]
    if not assignment_exists:
        return edhub_errors.AssignmentNotFoundException(course_id, assignment_id)
    return None


def assert_assignment_exists(conn, course_id: str, assignment_id: str):
    err = value_assert_assignment_exists(conn, course_id, assignment_id)
    if err is not None:
        raise err


def check_assignment_exists(conn, course_id: str, assignment_id: str) -> bool:
    return value_assert_assignment_exists(conn, course_id, assignment_id) is None


def value_assert_course_access(conn, user_email: str, course_id: str) -> Union[None, EdHubException]:
    err = value_assert_user_exists(conn, user_email)
    if err is not None:
        return err
    err = value_assert_course_exists(conn, course_id)
    if err is not None:
        return err
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1 FROM teaches WHERE email = %s AND courseid = %s
                UNION
                SELECT 1 FROM student_at WHERE email = %s AND courseid = %s
                UNION
                SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND courseid = %s
                UNION
                SELECT 1 FROM users WHERE email = %s AND isadmin
            )
        """,
            (user_email, course_id, user_email, course_id, user_email, course_id, user_email),
        )
        has_access = db_cursor.fetchone()[0]
    if not has_access:
        return edhub_errors.NoAccessToCourseException(course_id, user_email)
    return None


def assert_course_access(conn, user_email: str, course_id: str):
    err = value_assert_course_access(conn, user_email, course_id)
    if err is not None:
        raise err


def check_course_access(conn, user_email: str, course_id: str) -> bool:
    return value_assert_course_access(conn, user_email, course_id) is None


def value_assert_teacher_access(conn, teacher_email: str, course_id: str) -> Union[None, EdHubException]:
    err = value_assert_user_exists(conn, teacher_email)
    if err is not None:
        return err
    err = value_assert_course_exists(conn, course_id)
    if err is not None:
        return err
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1 FROM teaches WHERE email = %s AND courseid = %s
                UNION
                SELECT 1 FROM users WHERE email = %s AND isadmin
            )
        """,
            (teacher_email, course_id, teacher_email),
        )
        has_access = db_cursor.fetchone()[0]
    if not has_access:
        return edhub_errors.UserIsNotTeacherInCourseException(course_id, teacher_email)
    return None


def assert_teacher_access(conn, teacher_email: str, course_id: str):
    err = value_assert_teacher_access(conn, teacher_email, course_id)
    if err is not None:
        raise err


def check_teacher_access(conn, teacher_email: str, course_id: str) -> bool:
    return value_assert_teacher_access(conn, teacher_email, course_id) is None


def value_assert_student_access(conn, student_email: str, course_id: str) -> Union[None, EdHubException]:
    err = value_assert_user_exists(conn, student_email)
    if err is not None:
        return err
    err = value_assert_course_exists(conn, course_id)
    if err is not None:
        return err
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1 FROM student_at WHERE email = %s AND courseid = %s
                UNION
                SELECT 1 FROM users WHERE email = %s AND isadmin
            )
        """,
            (student_email, course_id, student_email),
        )
        has_access = db_cursor.fetchone()[0]
    if not has_access:
        return edhub_errors.UserIsNotStudentInCourseException(course_id, student_email)
    return None


def assert_student_access(conn, student_email: str, course_id: str):
    err = value_assert_student_access(conn, student_email, course_id)
    if err is not None:
        raise err


def check_student_access(conn, student_email: str, course_id: str) -> bool:
    return value_assert_student_access(conn, student_email, course_id) is None


def value_assert_parent_access(conn, parent_email: str, course_id: str) -> Union[None, EdHubException]:
    err = value_assert_user_exists(conn, parent_email)
    if err is not None:
        return err
    err = value_assert_course_exists(conn, course_id)
    if err is not None:
        return err
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND courseid = %s
                UNION
                SELECT 1 FROM users WHERE email = %s AND isadmin
            )
        """,
            (parent_email, course_id, parent_email),
        )
        has_access = db_cursor.fetchone()[0]
    if not has_access:
        return edhub_errors.UserIsNotParentInCourseException(course_id, parent_email)
    return None


def assert_parent_access(conn, parent_email: str, course_id: str):
    err = value_assert_parent_access(conn, parent_email, course_id)
    if err is not None:
        raise err


def check_parent_access(conn, parent_email: str, course_id: str) -> bool:
    return value_assert_parent_access(conn, parent_email, course_id) is None


def value_assert_parent_student_access(
    conn, parent_email: str, student_email: str, course_id: str
) -> Union[None, EdHubException]:
    err = value_assert_user_exists(conn, parent_email)
    if err is not None:
        return err
    err = value_assert_user_exists(conn, student_email)
    if err is not None:
        return err
    err = value_assert_course_exists(conn, course_id)
    if err is not None:
        return err
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND studentemail = %s AND courseid = %s
                UNION
                SELECT 1 FROM users WHERE email = %s AND isadmin
            )
        """,
            (parent_email, student_email, course_id, parent_email),
        )
        has_access = db_cursor.fetchone()[0]
    if not has_access:
        return edhub_errors.UserIsNotParentOfStudentInCourseException(course_id, parent_email, student_email)
    return None


def assert_parent_student_access(conn, parent_email: str, student_email: str, course_id: str):
    err = value_assert_parent_student_access(conn, parent_email, student_email, course_id)
    if err is not None:
        raise err


def check_parent_student_access(conn, parent_email: str, student_email: str, course_id: str) -> bool:
    return value_assert_parent_student_access(conn, parent_email, student_email, course_id) is None


def value_assert_submission_exists(
    conn, course_id: str, assignment_id: str, student_email: str
) -> Union[None, EdHubException]:
    err = value_assert_assignment_exists(conn, course_id, assignment_id)
    if err is not None:
        return err
    err = value_assert_student_access(conn, student_email, course_id)
    if err is not None:
        return err
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM course_assignments_submissions WHERE courseid = %s AND assid = %s AND email = %s)",
            (course_id, int(assignment_id), student_email),
        )
        submitted = db_cursor.fetchone()[0]
    if not submitted:
        return edhub_errors.NoSubmissionToAssignmentException(course_id, assignment_id, student_email)
    return None


def assert_submission_exists(conn, course_id: str, assignment_id: str, student_email: str):
    err = value_assert_submission_exists(conn, course_id, assignment_id, student_email)
    if err is not None:
        raise err


def check_submission_exists(conn, course_id: str, assignment_id: str, student_email: str) -> bool:
    return value_assert_submission_exists(conn, course_id, assignment_id, student_email) is None


def value_assert_parent_of_all(conn, parent_email: str,
                               student_emails: list[str], course_id: str) -> Union[None, EdHubException]:
    err = value_assert_user_exists(conn, parent_email)
    if err is not None:
        return err
    err = value_assert_course_exists(conn, course_id)
    if err is not None:
        return err
    if check_admin_access(conn, parent_email):
        return None
    with conn.cursor() as db_cursor:
        for student in student_emails:
            err = value_assert_user_exists(db_cursor, student)
            if err is not None:
                return err
            ok = sql.parents.sql_has_child_at_course(db_cursor, course_id, parent_email, student)
            if not ok:
                return edhub_errors.UserIsNotParentOfStudentInCourseException(course_id, parent_email, student)
    return None


def assert_parent_of_all(conn, parent_email: str, student_emails: list[str], course_id: str):
    err = value_assert_parent_of_all(conn, parent_email, student_emails, course_id)
    if err is not None:
        raise err


def check_parent_of_all(conn, parent_email: str, student_emails: list[str], course_id: str) -> bool:
    return value_assert_parent_of_all(conn, parent_email, student_emails, course_id) is None


def value_assert_admin_access(conn, user_email: str) -> Union[None, EdHubException]:
    err = value_assert_user_exists(conn, user_email)
    if err is not None:
        return err
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users WHERE email = %s AND isadmin)", (user_email,)
        )
        has_access = db_cursor.fetchone()[0]
    if not has_access:
        return edhub_errors.NotAnAdminException(user_email)
    return None


def assert_admin_access(conn, user_email: str):
    err = value_assert_admin_access(conn, user_email)
    if err is not None:
        raise err


def check_admin_access(conn, user_email: str) -> bool:
    return value_assert_admin_access(conn, user_email) is None


def value_assert_file_exists(storage_conn, file_id: str) -> Union[None, EdHubException]:
    with storage_conn.cursor() as db_cursor:
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM files WHERE id = %s)", (file_id,))
        if db_cursor.fetchone()[0]:
            return None
    return edhub_errors.AttachmentNotFoundException(file_id)


def assert_file_exists(storage_conn, file_id: str):
    err = value_assert_file_exists(storage_conn, file_id)
    if err is not None:
        raise err


def check_file_exists(storage_conn, file_id: str) -> bool:
    return value_assert_file_exists(storage_conn, file_id) is None


def value_assert_assignment_attachment_exists(conn, course_id: str, assignment_id: int, file_id: str) -> Union[None, EdHubException]:
    err = value_assert_assignment_exists(conn, course_id, assignment_id)
    if err is not None:
        return err
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """SELECT EXISTS (SELECT 1 FROM assignment_files WHERE courseid = %s AND
            assid = %s AND fileid = %s)""", (course_id, assignment_id, file_id)
        )
        if db_cursor.fetchone()[0]:
            return None
    return edhub_errors.AttachmentNotFoundInAssignmentException(course_id, assignment_id, file_id)


def assert_assignment_attachment_exists(conn, course_id: str, assignment_id: int, file_id: str):
    err = value_assert_assignment_attachment_exists(conn, course_id, assignment_id, file_id)
    if err is not None:
        raise err


def check_assignment_attachment_exists(conn, course_id: str, assignment_id: int, file_id: str) -> bool:
    return value_assert_assignment_attachment_exists(conn, course_id, assignment_id, file_id) is None


def value_assert_material_attachment_exists(conn, course_id: str, material_id: int, file_id: str) -> Union[None, EdHubException]:
    err = value_assert_material_exists(conn, course_id, material_id)
    if err is not None:
        return err
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """SELECT EXISTS (SELECT 1 FROM material_files WHERE courseid = %s AND
            matid = %s AND fileid = %s)""", (course_id, material_id, file_id)
        )
        if db_cursor.fetchone()[0]:
            return None
    return edhub_errors.AttachmentNotFoundInMaterialException(course_id, material_id, file_id)


def assert_material_attachment_exists(conn, course_id: str, material_id: int, file_id: str):
    err = value_assert_material_attachment_exists(conn, course_id, material_id, file_id)
    if err is not None:
        raise err


def check_material_attachment_exists(conn, course_id: str, material_id: int, file_id: str) -> bool:
    return value_assert_material_attachment_exists(conn, course_id, material_id, file_id) is None
