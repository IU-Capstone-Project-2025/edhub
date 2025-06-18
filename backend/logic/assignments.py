from fastapi import HTTPException
from constants import TIME_FORMAT
import constraints
import repo.assignments as repo_ass


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

    # create assignment
    assignment_id = repo_ass.sql_insert_assignment(
        db_cursor, course_id, title, description, user_email
    )

    return {"course_id": course_id, "assignment_id": assignment_id}


def remove_assignment(
    db_conn, db_cursor, course_id: str, assignment_id: str, user_email: str
):
    # checking constraints
    constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # remove students' submissions
    repo_ass.sql_delete_assignment_submissions(db_cursor, course_id, assignment_id)

    # reomve assignment
    repo_ass.sql_delete_assignment(db_cursor, course_id, assignment_id)

    return {"success": True}


def get_assignment(db_cursor, course_id: str, assignment_id: str, user_email: str):

    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # searching for assignments
    assignment = repo_ass.sql_select_assignment(db_cursor, course_id, assignment_id)
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

    submission = repo_ass.sql_select_submission_grade(
        db_cursor, course_id, assignment_id, student_email
    )

    # inserting submission
    if submission is None:
        repo_ass.sql_insert_submission(
            db_cursor, course_id, assignment_id, student_email, comment
        )
        db_conn.commit()

    # updating submission if not graded
    elif submission and submission[0] in (None, "null"):
        repo_ass.sql_update_submission_comment(
            db_cursor, comment, course_id, assignment_id, student_email
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
    submissions = repo_ass.sql_select_submissions(db_cursor, course_id, assignment_id)

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
    if not (
        constraints.check_teacher_access(
            db_cursor, user_email, course_id
        ) or constraints.check_parent_student_access(
            db_cursor, user_email, student_email, course_id
        ) or student_email == user_email
    ):
        raise HTTPException(
            status_code=403, detail="User does not have access to this submission"
        )

    # finding student's submission
    submission = repo_ass.sql_select_single_submission(
        db_cursor, course_id, assignment_id, student_email
    )
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
    constraints.assert_teacher_access(db_cursor, user_email, course_id)
    constraints.assert_submission_exists(db_cursor, course_id, assignment_id, student_email)

    repo_ass.sql_update_submission_grade(
        db_cursor, grade, user_email, course_id, assignment_id, student_email
    )
    db_conn.commit()

    return {"success": True}
