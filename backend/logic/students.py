from fastapi import HTTPException
import constraints


def get_enrolled_students(db_cursor, course_id: str, user_email: str):
    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # finding enrolled students
    db_cursor.execute(
        """
        SELECT
            s.email,
            u.publicname
        FROM student_at s
        JOIN users u ON s.email = u.email
        WHERE s.courseid = %s
    """,
        (course_id,),
    )
    students = db_cursor.fetchall()

    res = [{"email": st[0], "name": st[1]} for st in students]
    return res


def invite_student(
    db_conn, db_cursor, course_id: str, student_email: str, teacher_email: str
):
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
        raise HTTPException(
            status_code=403, detail="Can't invite course teacher as a student"
        )

    # check if the potential student already has parent rights at this course
    if constraints.check_parent_access(db_cursor, student_email, course_id):
        raise HTTPException(status_code=403, detail="Can't invite parent as a student")

    # invite student
    db_cursor.execute(
        "INSERT INTO student_at (email, courseid) VALUES (%s, %s)",
        (student_email, course_id),
    )
    db_conn.commit()

    return {"success": True}


def remove_student(
    db_conn, db_cursor, course_id: str, student_email: str, teacher_email: str
):
    # checking constraints
    constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

    # check if the student is enrolled to course
    if not constraints.check_student_access(db_cursor, student_email, course_id):
        raise HTTPException(
            status_code=404, detail="User to remove is not a student at this course"
        )

    # remove student
    db_cursor.execute(
        "DELETE FROM student_at WHERE courseid = %s AND email = %s",
        (course_id, student_email),
    )

    # remove student's parents
    db_cursor.execute(
        "DELETE FROM parent_of_at_course WHERE courseid = %s AND studentemail = %s",
        (course_id, student_email),
    )
    db_conn.commit()

    return {"success": True}
