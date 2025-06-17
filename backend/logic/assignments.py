from fastapi import HTTPException
from constants import TIME_FORMAT
import constraints


def create_assignment(
    db_conn,
    db_cursor,
    course_id: str,
    title: str,
    description: str,
    user_email: str,
):
    # checking constraints
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # create material
    db_cursor.execute(
        "INSERT INTO course_assignments (courseid, name, description, timeadded, author) VALUES (%s, %s, %s, now(), %s) RETURNING assid",
        (course_id, title, description, user_email),
    )
    assignment_id = db_cursor.fetchone()[0]
    db_conn.commit()

    return {"course_id": course_id, "assignment_id": assignment_id}


def remove_assignment(
    db_conn, db_cursor, course_id: str, assignment_id: str, user_email: str
):
    # checking constraints
    constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # remove material
    db_cursor.execute(
        "DELETE FROM course_assignments WHERE courseid = %s AND assid = %s",
        (course_id, assignment_id),
    )
    db_conn.commit()

    # remove students' submissions
    db_cursor.execute(
        "DELETE FROM course_assignments_submissions WHERE courseid = %s AND assid = %s",
        (course_id, assignment_id),
    )
    db_conn.commit()

    return {"success": True}


def get_assignment(db_cursor, course_id: str, assignment_id: str, user_email: str):

    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # searching for assignments
    db_cursor.execute(
        """
        SELECT courseid, assid, timeadded, name, description, author
        FROM course_assignments
        WHERE courseid = %s AND assid = %s
    """,
        (course_id, assignment_id),
    )
    assignment = db_cursor.fetchone()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    res = {
        "course_id": str(assignment[0]),
        "assignment_id": assignment[1],
        "creation_time": assignment[2].strftime(TIME_FORMAT),
        "title": assignment[3],
        "description": assignment[4],
        "author": assignment[5],
    }
    return res


def submit_assignment(
    db_conn,
    db_cursor,
    course_id: str,
    assignment_id: str,
    comment: str,
    student_email: str,
):

    # checking constraints
    constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
    constraints.assert_student_access(db_cursor, student_email, course_id)

    db_cursor.execute(
        "SELECT grade FROM course_assignments_submissions WHERE courseid = %s AND assid = %s AND email = %s",
        (course_id, assignment_id, student_email),
    )
    submission = db_cursor.fetchone()

    # inserting submission
    if submission is None:
        db_cursor.execute(
            "INSERT INTO course_assignments_submissions (courseid, assid, email, timeadded, timemodified, comment, grade, gradedby) VALUES (%s, %s, %s, now(), now(), %s, null, null)",
            (course_id, assignment_id, student_email, comment),
        )
        db_conn.commit()

    # updating submission if not graded
    elif submission and submission[0] in (None, "null"):
        db_cursor.execute(
            """
            UPDATE course_assignments_submissions
            SET comment = %s, timemodified = now()
            WHERE courseid = %s AND assid = %s AND email = %s
        """,
            (comment, course_id, assignment_id, student_email),
        )
        db_conn.commit()

    else:
        raise HTTPException(
            status_code=404, detail="Can't edit the submission after it was graded."
        )

    return {"success": True}


def get_assignment_submissions(
    db_cursor, course_id: str, assignment_id: str, user_email: str
):
    # checking constraints
    constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # finding students' submissions
    db_cursor.execute(
        """
        SELECT
            s.email,
            u.publicname,
            s.timeadded,
            s.timemodified,
            s.comment,
            s.grade,
            s.gradedby
        FROM course_assignments_submissions s
        JOIN users u ON s.email = u.email
        WHERE s.courseid = %s AND s.assid = %s
        ORDER BY s.timeadded DESC
    """,
        (course_id, assignment_id),
    )
    submissions = db_cursor.fetchall()

    res = [
        {
            "course_id": course_id,
            "assignment_id": assignment_id,
            "student_email": sub[0],
            "student_name": sub[1],
            "submission_time": sub[2].strftime(TIME_FORMAT),
            "last_modification_time": sub[3].strftime(TIME_FORMAT),
            "comment": sub[4],
            "grade": sub[5],
            "gradedby_email": sub[6],
        }
        for sub in submissions
    ]
    return res


def get_submission(
    db_cursor,
    course_id: str,
    assignment_id: str,
    student_email: str,
    user_email: str,
):
    # checking constraints
    constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
    constraints.assert_student_access(db_cursor, student_email, course_id)
    if (
        not constraints.check_teacher_access(db_cursor, user_email, course_id)
        and not constraints.check_parent_student_access(
            db_cursor, user_email, student_email, course_id
        )
        and not student_email == user_email
    ):
        raise HTTPException(
            status_code=403, detail="User does not have access to this submission"
        )

    # finding student's submission
    db_cursor.execute(
        """
        SELECT
            s.email,
            u.publicname,
            s.timeadded,
            s.timemodified,
            s.comment,
            s.grade,
            s.gradedby
        FROM course_assignments_submissions s
        JOIN users u ON s.email = u.email
        WHERE s.courseid = %s AND s.assid = %s AND s.email = %s
    """,
        (course_id, assignment_id, student_email),
    )
    submission = db_cursor.fetchone()
    if not submission:
        raise HTTPException(
            status_code=404, detail="Submission of this user is not found"
        )

    res = {
        "course_id": course_id,
        "assignment_id": assignment_id,
        "student_email": submission[0],
        "student_name": submission[1],
        "submission_time": submission[2].strftime(TIME_FORMAT),
        "last_modification_time": submission[3].strftime(TIME_FORMAT),
        "comment": submission[4],
        "grade": submission[5],
        "gradedby_email": submission[6],
    }
    return res


def grade_submission(
    db_conn,
    db_cursor,
    course_id: str,
    assignment_id: str,
    student_email: str,
    grade: str,
    user_email: str,
):
    # checking constraints
    constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # check if the student is enrolled to course
    if not constraints.check_student_access(db_cursor, student_email, course_id):
        raise HTTPException(
            status_code=403, detail="Provided user in not a student at this course"
        )

    # TODO: this is not implemented in the constraints??????????
    # check submission of student exists
    # constraints.assert_submission_exists(
    #     db_cursor, course_id, assignment_id, student_email
    # )

    # grading submission
    db_cursor.execute(
        """
        UPDATE course_assignments_submissions
        SET grade = %s, gradedby = %s
        WHERE courseid = %s AND assid = %s AND email = %s
    """,
        (grade, user_email, course_id, assignment_id, student_email),
    )
    db_conn.commit()

    return {"success": True}
