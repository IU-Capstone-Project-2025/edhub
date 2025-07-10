import edhub_errors
import constraints
import sql.teachers as sql_teachers
import logic.logging as logger


def get_course_teachers(db_conn, course_id: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_course_access(db_cursor, user_email, course_id)

        teachers = sql_teachers.select_course_teachers(db_cursor, course_id)

        res = [{"email": tch[0], "name": tch[1]} for tch in teachers]
        return res


def invite_teacher(db_conn, course_id: str, new_teacher_email: str, teacher_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_user_exists(db_cursor, new_teacher_email)
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

        if constraints.check_teacher_access(db_cursor, new_teacher_email, course_id):
            raise edhub_errors.UserAlreadyTeacherException(course_id, new_teacher_email)

        if constraints.check_student_access(db_cursor, new_teacher_email, course_id):
            raise edhub_errors.UserAlreadyHasDifferentRoleException(
                course_id, new_teacher_email, edhub_errors.ROLE_STUDENT, edhub_errors.ROLE_TEACHER
            )

        if constraints.check_parent_access(db_cursor, new_teacher_email, course_id):
            raise edhub_errors.UserAlreadyHasDifferentRoleException(
                course_id, new_teacher_email, edhub_errors.ROLE_PARENT, edhub_errors.ROLE_TEACHER
            )

        sql_teachers.insert_teacher(db_cursor, new_teacher_email, course_id)
        db_conn.commit()

        logger.log(db_conn, logger.TAG_TEACHER_ADD, f"Teacher {teacher_email} invited a teacher {new_teacher_email}")

        return {"success": True}


def remove_teacher(db_conn, course_id: str, removing_teacher_email: str, teacher_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_user_exists(db_cursor, removing_teacher_email)
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)
        constraints.assert_teacher_access(db_cursor, removing_teacher_email, course_id)
        teachers_left = sql_teachers.count_teachers(db_cursor, course_id)
        if teachers_left == 1:
            raise edhub_errors.CannotRemoveLastTeacher(course_id, removing_teacher_email)

        sql_teachers.delete_teacher(db_cursor, course_id, removing_teacher_email)
        db_conn.commit()

        logger.log(
            db_conn, logger.TAG_TEACHER_DEL, f"Teacher {teacher_email} removed a teacher {removing_teacher_email}"
        )

        return {"success": True}
