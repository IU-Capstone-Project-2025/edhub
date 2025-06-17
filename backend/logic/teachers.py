from fastapi import HTTPException
import constraints
import repo.teachers as repo_teachers


def get_course_teachers(db_cursor, course_id: str, user_email: str):
    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # finding assigned teachers
    teachers = repo_teachers.sql_select_course_teachers(db_cursor, course_id)

    res = [{"email": tch[0], "name": tch[1]} for tch in teachers]
    return res


def invite_teacher(
    db_conn, db_cursor, course_id: str, new_teacher_email: str, teacher_email: str
):
    # checking constraints
    constraints.assert_user_exists(db_cursor, new_teacher_email)
    constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

    # check if the teacher already assigned to course
    if constraints.check_teacher_access(db_cursor, new_teacher_email, course_id):
        raise HTTPException(
            status_code=403,
            detail="User to invite already has teacher right at this course",
        )

    # check if the potential teacher already has student rights at this course
    if constraints.check_student_access(db_cursor, new_teacher_email, course_id):
        raise HTTPException(
            status_code=403, detail="Can't invite course student as a teacher"
        )

    # check if the potential teacher already has parent rights at this course
    if constraints.check_parent_access(db_cursor, new_teacher_email, course_id):
        raise HTTPException(status_code=403, detail="Can't invite parent as a teacher")

    # invite teacher
    repo_teachers.sql_insert_teacher(db_cursor, new_teacher_email, course_id)
    db_conn.commit()

    return {"success": True}


def remove_teacher(
    db_conn, db_cursor, course_id: str, removing_teacher_email: str, teacher_email: str
):
    # checking constraints
    constraints.assert_user_exists(db_cursor, removing_teacher_email)
    constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

    # check if the teacher assigned to the course
    if not constraints.check_teacher_access(
        db_cursor, removing_teacher_email, course_id
    ):
        raise HTTPException(
            status_code=403, detail="User to remove is not a teacher at this course"
        )

    # ensuring that at least one teacher remains in the course
    teachers_left = repo_teachers.sql_count_teachers(db_cursor, course_id)
    if teachers_left == 1:
        raise HTTPException(
            status_code=404, detail="Cannot remove the last teacher at the course"
        )

    # remove teacher
    repo_teachers.sql_delete_teacher(db_cursor, course_id, removing_teacher_email)
    db_conn.commit()

    return {"success": True}
