import edhub_errors
import constraints
import sql.parents as sql_parents
import logic.logging as logger
import logic.users


def get_students_parents(db_conn, course_id: str, student_email: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        constraints.assert_student_access(db_cursor, student_email, course_id)

        parents = sql_parents.select_students_parents(db_cursor, course_id, student_email)

        res = [{"email": par[0], "name": par[1]} for par in parents]
        return res


def invite_parent(
    db_conn,
    course_id: str,
    student_email: str,
    parent_email: str,
    teacher_email: str,
):
    with db_conn.cursor() as db_cursor:
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)
        constraints.assert_student_access(db_cursor, student_email, course_id)

        if constraints.check_parent_student_access(db_cursor, parent_email, student_email, course_id):
            raise edhub_errors.UserIsAlreadyParentOfStudentInCourseException(course_id, parent_email, student_email)

    roles = logic.users.get_user_role(db_conn, course_id, parent_email)
    if roles["is_teacher"]:
        raise edhub_errors.UserAlreadyHasDifferentRoleException(course_id, parent_email, edhub_errors.ROLE_TEACHER, edhub_errors.ROLE_PARENT)
    if roles["is_student"]:
        raise edhub_errors.UserAlreadyHasDifferentRoleException(course_id, parent_email, edhub_errors.ROLE_STUDENT, edhub_errors.ROLE_PARENT)

    with db_conn.cursor() as db_cursor:
        sql_parents.insert_parent_of_at_course(db_cursor, parent_email, student_email, course_id)
        db_conn.commit()

        logger.log(
            db_conn,
            logger.TAG_PARENT_ADD,
            f"Teacher {teacher_email} invited a parent {parent_email} for student {student_email}",
        )

    return {"success": True}


def remove_parent(
    db_conn,
    course_id: str,
    student_email: str,
    parent_email: str,
    user_email: str,
):
    with db_conn.cursor() as db_cursor:
        if not (
            constraints.check_admin_access(db_cursor, user_email)
            or constraints.check_teacher_access(db_cursor, user_email, course_id)
            or (constraints.check_parent_access(db_cursor, user_email, course_id) and parent_email == user_email)
        ):
            raise edhub_errors.CannotRemoveParentException(course_id, user_email, parent_email)

        constraints.assert_parent_student_access(db_cursor, parent_email, student_email, course_id)

        sql_parents.delete_parent_of_at_course(db_cursor, course_id, student_email, parent_email)
        db_conn.commit()

        logger.log(
            db_conn,
            logger.TAG_PARENT_DEL,
            f"Teacher {user_email} removed a parent {parent_email} for student {student_email}",
        )

        return {"success": True}


def get_parents_children(db_conn, course_id: str, user_email: str):
    with db_conn.cursor() as db_cursor:
        constraints.assert_course_exists(db_cursor, course_id)

        parents_children = sql_parents.select_parents_children(db_cursor, course_id, user_email)

        res = [{"email": child[0], "name": child[1]} for child in parents_children]
        return res
