import edhub_errors
import constraints
import sql.teachers as sql_teachers


get_course_teachers = sql_teachers.select_course_teachers


def invite_teacher(conn, course_id: str, new_teacher_email: str):
    constraints.assert_user_exists(conn, new_teacher_email)
    if constraints.check_teacher_access(conn, new_teacher_email, course_id):
        raise edhub_errors.UserAlreadyTeacherException(course_id, new_teacher_email)
    if constraints.check_student_access(conn, new_teacher_email, course_id):
        raise edhub_errors.UserAlreadyHasDifferentRoleException(
            course_id, new_teacher_email, edhub_errors.ROLE_STUDENT, edhub_errors.ROLE_TEACHER
        )
    if constraints.check_parent_access(conn, new_teacher_email, course_id):
        raise edhub_errors.UserAlreadyHasDifferentRoleException(
            course_id, new_teacher_email, edhub_errors.ROLE_PARENT, edhub_errors.ROLE_TEACHER
        )
    sql_teachers.insert_teacher(conn, new_teacher_email, course_id)


def remove_teacher(conn, course_id: str, removing_teacher_email: str):
    constraints.assert_teacher_access(conn, removing_teacher_email, course_id)
    teachers_left = sql_teachers.count_teachers(conn, course_id)
    if teachers_left == 1:
        raise edhub_errors.CannotRemoveLastTeacher(course_id, removing_teacher_email)
    sql_teachers.delete_teacher(conn, course_id, removing_teacher_email)
