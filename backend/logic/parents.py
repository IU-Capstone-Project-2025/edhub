import edhub_errors
import constraints
import sql.parents as sql_parents
from sql.dto import UserEmailNameDTO


get_students_parents = sql_parents.select_students_parents


def invite_parent(
    db_conn,
    course_id: str,
    student_email: str,
    parent_email: str,
    teacher_email: str,
) -> None:
    if constraints.check_parent_student_access(db_conn, parent_email, student_email, course_id):
        raise edhub_errors.UserIsAlreadyParentOfStudentInCourseException(course_id, parent_email, student_email)

    if constraints.check_teacher_access(db_conn, parent_email, course_id):
        raise edhub_errors.UserAlreadyHasDifferentRoleException(course_id, parent_email, edhub_errors.ROLE_TEACHER, edhub_errors.ROLE_PARENT)
    if constraints.check_student_access(db_conn, parent_email, course_id):
        raise edhub_errors.UserAlreadyHasDifferentRoleException(course_id, parent_email, edhub_errors.ROLE_STUDENT, edhub_errors.ROLE_PARENT)

    sql_parents.insert_parent_of_at_course(db_conn, parent_email, student_email, course_id)


def remove_parent(
    db_conn,
    course_id: str,
    student_email: str,
    parent_email: str,
    user_email: str,
) -> None:
    constraints.assert_parent_student_access(db_conn, parent_email, student_email, course_id)
    sql_parents.delete_parent_of_at_course(db_conn, course_id, student_email, parent_email)


def get_parents_children(db_conn, course_id: str, user_email: str) -> list[UserEmailNameDTO]:
    constraints.assert_course_exists(db_conn, course_id)
    return sql_parents.select_parents_children(db_conn, course_id, user_email)
