from fastapi import HTTPException
import constraints
import repo.parents as repo_parents


def get_students_parents(db_cursor, course_id: str, student_email: str, user_email: str):

    # checking constraints
    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # check if the student is enrolled to course
    if not constraints.check_student_access(db_cursor, student_email, course_id):
        raise HTTPException(status_code=404, detail="Provided user in not a student at this course")

    # finding student's parents
    parents = repo_parents.sql_select_students_parents(db_cursor, course_id, student_email)

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
    if constraints.check_parent_student_access(db_cursor, parent_email, student_email, course_id):
        raise HTTPException(status_code=403, detail="Parent already assigned to this student at this course")

    # check if the potential parent already has teacher rights at this course
    if constraints.check_teacher_access(db_cursor, parent_email, course_id):
        raise HTTPException(status_code=403, detail="Can't invite course teacher as a parent")

    # check if the potential parent already has student rights at this course
    if constraints.check_student_access(db_cursor, parent_email, course_id):
        raise HTTPException(status_code=403, detail="Can't invite course student as a parent")

    # invite parent
    repo_parents.sql_insert_parent_of_at_course(db_cursor, parent_email, student_email, course_id)
    db_conn.commit()

    return {"success": True}


def remove_parent(
    db_conn,
    db_cursor,
    course_id: str,
    student_email: str,
    parent_email: str,
    user_email: str,
):

    # checking constraints
    if not (
        constraints.check_teacher_access(db_cursor, user_email, course_id) or
        (constraints.check_parent_access(db_cursor, user_email, course_id) and parent_email == user_email)
    ):
        raise HTTPException(status_code=403, detail="User does not have permissions to delete this parent")

    # check if the parent assigned to the course with the student
    constraints.assert_parent_student_access(db_cursor, parent_email, student_email, course_id)

    # remove parent
    repo_parents.sql_delete_parent_of_at_course(db_cursor, course_id, student_email, parent_email)
    db_conn.commit()

    return {"success": True}


def get_parents_children(db_cursor, course_id: str, user_email: str):

    # checking constraints
    constraints.assert_course_exists(db_cursor, course_id)

    parents_children = repo_parents.sql_select_parents_children(db_cursor, course_id, user_email)

    res = [{"email": child[0], "name": child[1]} for child in parents_children]
    return res
