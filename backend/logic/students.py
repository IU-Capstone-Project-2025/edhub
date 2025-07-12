import edhub_errors
import constraints
import sql.students as sql_students


get_enrolled_students = sql_students.select_enrolled_students


def invite_student(conn, course_id: str, student_email: str, teacher_email: str) -> None:
    constraints.assert_user_exists(conn, student_email)

    if constraints.check_student_access(conn, student_email, course_id):
        raise edhub_errors.UserAlreadyStudentException(course_id, student_email)
    if constraints.check_teacher_access(conn, student_email, course_id):
        raise edhub_errors.UserAlreadyHasDifferentRoleException(
            course_id, student_email, edhub_errors.ROLE_TEACHER, edhub_errors.ROLE_STUDENT
        )
    if constraints.check_parent_access(conn, student_email, course_id):
        raise edhub_errors.UserAlreadyHasDifferentRoleException(
            course_id, student_email, edhub_errors.ROLE_PARENT, edhub_errors.ROLE_STUDENT
        )

    sql_students.insert_student_at(conn, student_email, course_id)


def remove_student(conn, course_id: str, student_email: str) -> None:
    constraints.assert_student_access(conn, student_email, course_id)
    sql_students.delete_student_at(conn, course_id, student_email)
