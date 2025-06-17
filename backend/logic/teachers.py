from fastapi import HTTPException
import constraints


def get_course_teachers(db_cursor, course_id: str, user_email: str):
    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # finding assigned teachers
    db_cursor.execute(
        """
        SELECT
            t.email,
            u.publicname
        FROM teaches t
        JOIN users u ON t.email = u.email
        WHERE t.courseid = %s
        GROUP BY t.email, u.publicname
    """,
        (course_id,),
    )
    teachers = db_cursor.fetchall()

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
    db_cursor.execute(
        "INSERT INTO teaches (email, courseid) VALUES (%s, %s)",
        (new_teacher_email, course_id),
    )
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
    db_cursor.execute("SELECT COUNT(*) FROM teaches WHERE courseid = %s", (course_id,))
    teachers_left = db_cursor.fetchone()[0]
    if teachers_left == 1:
        raise HTTPException(
            status_code=404, detail="Cannot remove the last teacher at the course"
        )

    # remove teacher
    db_cursor.execute(
        "DELETE FROM teaches WHERE courseid = %s AND email = %s",
        (course_id, removing_teacher_email),
    )
    db_conn.commit()

    return {"success": True}
