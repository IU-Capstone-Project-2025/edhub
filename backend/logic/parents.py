from fastapi import HTTPException
import constraints


def get_students_parents(
    db_cursor, course_id: str, student_email: str, user_email: str
):

    # checking constraints
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # check if the student is enrolled to course
    if not constraints.check_student_access(db_cursor, student_email, course_id):
        raise HTTPException(
            status_code=404, detail="Provided user in not a student at this course"
        )

    # finding student's parents
    db_cursor.execute(
        """
        SELECT
            p.parentemail,
            u.publicname
        FROM parent_of_at_course p
        JOIN users u ON p.parentemail = u.email
        WHERE p.courseid = %s AND p.studentemail = %s
    """,
        (course_id, student_email),
    )
    parents = db_cursor.fetchall()

    res = [{"email": par[0], "name": par[1]} for par in parents]
    return res


def invite_parent(
    db_conn,
    db_cursor,
    course_id: str,
    student_email: str,
    parent_email: str,
    teacher_email: str,
):

    # checking constraints
    constraints.assert_teacher_access(db_cursor, teacher_email, course_id)
    constraints.assert_student_access(db_cursor, student_email, course_id)

    # check if the parent already assigned to the course with the student
    if constraints.check_parent_student_access(
        db_cursor, parent_email, student_email, course_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Parent already assigned to this student at this course",
        )

    # check if the potential parent already has teacher rights at this course
    if constraints.check_teacher_access(db_cursor, parent_email, course_id):
        raise HTTPException(
            status_code=403, detail="Can't invite course teacher as a parent"
        )

    # check if the potential parent already has student rights at this course
    if constraints.check_student_access(db_cursor, parent_email, course_id):
        raise HTTPException(
            status_code=403, detail="Can't invite course student as a parent"
        )

    # invite parent
    db_cursor.execute(
        "INSERT INTO parent_of_at_course (parentemail, studentemail, courseid) VALUES (%s, %s, %s)",
        (parent_email, student_email, course_id),
    )
    db_conn.commit()

    return {"success": True}


def remove_parent(
    db_conn,
    db_cursor,
    course_id: str,
    student_email: str,
    parent_email: str,
    teacher_email: str,
):

    # checking constraints
    constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

    # check if the parent assigned to the course with the student
    constraints.assert_parent_student_access(
        db_cursor, parent_email, student_email, course_id
    )

    # remove parent
    db_cursor.execute(
        "DELETE FROM parent_of_at_course WHERE courseid = %s AND studentemail = %s AND parentemail = %s",
        (course_id, student_email, parent_email),
    )
    db_conn.commit()

    return {"success": True}


def get_parents_children(db_cursor, course_id: str, user_email: str):

    # checking constraints
    constraints.assert_course_exists(db_cursor, course_id)

    db_cursor.execute(
        """
        SELECT
            p.studentemail,
            u.publicname
        FROM parent_of_at_course p
        JOIN users u ON p.studentemail = u.email
        WHERE p.courseid = %s AND p.parentemail = %s
    """,
        (course_id, user_email),
    )
    parents_children = db_cursor.fetchall()  # Renamed variable for clarity

    res = [{"email": child[0], "name": child[1]} for child in parents_children]
    return res
