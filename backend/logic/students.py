from fastapi import HTTPException
import constraints
import sql.students as sql_students
import logic.logging as logger


def get_enrolled_students(db_cursor, course_id: str, user_email: str):
    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # finding enrolled students
    students = sql_students.select_enrolled_students(db_cursor, course_id)

    res = [{"email": st[0], "name": st[1]} for st in students]
    return res


def invite_student(db_conn, db_cursor, course_id: str, student_email: str, teacher_email: str):
    # checking constraints
    constraints.assert_user_exists(db_cursor, student_email)
    constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

    # check if the student already enrolled to course
    if constraints.check_student_access(db_cursor, student_email, course_id):
        raise HTTPException(
            status_code=403,
            detail="The invited user already has student rights in this course",
        )

    # check if the potential student already has teacher rights at this course
    if constraints.check_teacher_access(db_cursor, student_email, course_id):
        raise HTTPException(status_code=403, detail="Can't invite course teacher as a student")

    # check if the potential student already has parent rights at this course
    if constraints.check_parent_access(db_cursor, student_email, course_id):
        raise HTTPException(status_code=403, detail="Can't invite parent as a student")

    # invite student
    sql_students.insert_student_at(db_cursor, student_email, course_id)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_STUDENT_ADD, f"Teacher {teacher_email} invited a student {student_email}")
    return {"success": True}


def remove_student(db_conn, db_cursor, course_id: str, student_email: str, user_email: str):
    # checking constraints
    if not (
        constraints.check_teacher_access(db_cursor, user_email, course_id)
        or (constraints.check_student_access(db_cursor, user_email, course_id) and student_email == user_email)
    ):
        raise HTTPException(status_code=403, detail="User does not have permissions to delete this student")

    # check if the student is enrolled to course
    if not constraints.check_student_access(db_cursor, student_email, course_id):
        raise HTTPException(status_code=404, detail="User to remove is not a student at this course")

    # remove student
    sql_students.delete_student_at(db_cursor, course_id, student_email)
    db_conn.commit()

    logger.log(db_conn, logger.TAG_STUDENT_DEL, f"Teacher {user_email} removed a student {student_email}")

    return {"success": True}
