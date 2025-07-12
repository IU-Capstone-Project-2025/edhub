import edhub_errors
import constraints
import sql.students as sql_students


get_enrolled_students = sql_students.select_enrolled_students


def invite_student(db_conn, course_id: str, student_email: str, teacher_email: str) -> None:
    with db_conn.cursor() as db_cursor:
        constraints.assert_user_exists(db_cursor, student_email)

        if constraints.check_student_access(db_cursor, student_email, course_id):
            raise edhub_errors.UserAlreadyStudentException(course_id, student_email)
        if constraints.check_teacher_access(db_cursor, student_email, course_id):
            raise edhub_errors.UserAlreadyHasDifferentRoleException(
                course_id, student_email, edhub_errors.ROLE_TEACHER, edhub_errors.ROLE_STUDENT
            )
        if constraints.check_parent_access(db_cursor, student_email, course_id):
            raise edhub_errors.UserAlreadyHasDifferentRoleException(
                course_id, student_email, edhub_errors.ROLE_PARENT, edhub_errors.ROLE_STUDENT
            )

        sql_students.insert_student_at(db_cursor, student_email, course_id)


def remove_student(db_conn, course_id: str, student_email: str) -> None:
    constraints.assert_student_access(db_conn, student_email, course_id)
    sql_students.delete_student_at(db_conn, course_id, student_email)
