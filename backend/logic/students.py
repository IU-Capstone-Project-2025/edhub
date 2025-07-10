import edhub_errors
import constraints
import sql.students as sql_students
import logic.logging as logger


def get_enrolled_students(db_conn, course_id: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_course_access(db_cursor, user_email, course_id)
        students = sql_students.select_enrolled_students(db_cursor, course_id)
        res = [{"email": st[0], "name": st[1]} for st in students]
        return res


def invite_student(db_conn, course_id: str, student_email: str, teacher_email: str):
    with db_conn.cursor() as db_cursor:
        # checking constraints
        constraints.assert_user_exists(db_cursor, student_email)
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

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

        # invite student
        sql_students.insert_student_at(db_cursor, student_email, course_id)
        db_conn.commit()

        logger.log(db_conn, logger.TAG_STUDENT_ADD, f"Teacher {teacher_email} invited a student {student_email}")
        return {"success": True}


def remove_student(db_conn, course_id: str, student_email: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_student_access(db_cursor, student_email, course_id)
        if not (
            constraints.check_teacher_access(db_cursor, user_email, course_id)
            or (constraints.check_student_access(db_cursor, user_email, course_id) and student_email == user_email)
        ):
            raise edhub_errors.CannotRemoveStudentException(course_id, user_email, student_email)

        sql_students.delete_student_at(db_cursor, course_id, student_email)
        db_conn.commit()

        logger.log(db_conn, logger.TAG_STUDENT_DEL, f"Teacher {user_email} removed a student {student_email}")

        return {"success": True}
