from fastapi import HTTPException
import repository.users as users_repo
import repository.courses as courses_repo

# put function defintions related to the user logic here.
# these fucntions will be called by the api handlers.


def invite_student_logic(db_cursor, db_conn, course_id, student_email, teacher_email):
    courses_repo.assert_course_exists(db_cursor, course_id)
    users_repo.assert_user_exists(db_cursor, student_email)
    users_repo.assert_teacher_access(db_cursor, teacher_email, course_id)

    if users_repo.check_student_access(db_cursor, student_email, course_id):
        raise HTTPException(
            status_code=404,
            detail="User to invite already has student right at this course",
        )
    if users_repo.check_teacher_access(db_cursor, student_email, course_id):
        raise HTTPException(
            status_code=404, detail="Can't invite course teacher as a student"
        )
    if users_repo.check_parent_access(db_cursor, student_email, course_id):
        raise HTTPException(status_code=404, detail="Can't invite parent as a student")

    users_repo.add_student_to_course(db_cursor, db_conn, student_email, course_id)
    return {"success": True}


def remove_student_logic(db_cursor, db_conn, course_id, student_email, teacher_email):
    courses_repo.assert_course_exists(db_cursor, course_id)
    users_repo.assert_user_exists(db_cursor, student_email)
    users_repo.assert_teacher_access(db_cursor, teacher_email, course_id)

    if not users_repo.check_student_access(db_cursor, student_email, course_id):
        raise HTTPException(
            status_code=404, detail="User to remove is not a student at this course"
        )

    users_repo.remove_student_from_course(db_cursor, db_conn, student_email, course_id)
    users_repo.remove_student_parents(db_cursor, db_conn, student_email, course_id)
    return {"success": True}


def invite_parent_logic(
    db_cursor, db_conn, course_id, student_email, parent_email, teacher_email
):
    users_repo.assert_user_exists(db_cursor, student_email)
    users_repo.assert_user_exists(db_cursor, parent_email)
    courses_repo.assert_course_exists(db_cursor, course_id)
    users_repo.assert_teacher_access(db_cursor, teacher_email, course_id)
    users_repo.assert_student_access(db_cursor, student_email, course_id)

    if users_repo.check_parent_student_access(
        db_cursor, parent_email, student_email, course_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Parent already assigned to this student at this course",
        )
    if users_repo.check_teacher_access(db_cursor, parent_email, course_id):
        raise HTTPException(
            status_code=404, detail="Can't invite course teacher as a parent"
        )
    if users_repo.check_student_access(db_cursor, parent_email, course_id):
        raise HTTPException(
            status_code=404, detail="Can't invite course student as a parent"
        )

    users_repo.add_parent_to_student(
        db_cursor, db_conn, parent_email, student_email, course_id
    )
    return {"success": True}


def remove_parent_logic(
    db_cursor, db_conn, course_id, student_email, parent_email, teacher_email
):
    courses_repo.assert_course_exists(db_cursor, course_id)
    users_repo.assert_user_exists(db_cursor, student_email)
    users_repo.assert_user_exists(db_cursor, parent_email)
    users_repo.assert_teacher_access(db_cursor, teacher_email, course_id)

    if not users_repo.check_parent_student_access(
        db_cursor, parent_email, student_email, course_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Parent is not assigned to this student at this course",
        )

    users_repo.remove_parent_from_student(
        db_cursor, db_conn, parent_email, student_email, course_id
    )
    return {"success": True}


def invite_teacher_logic(
    db_cursor, db_conn, course_id, new_teacher_email, teacher_email
):
    courses_repo.assert_course_exists(db_cursor, course_id)
    users_repo.assert_user_exists(db_cursor, new_teacher_email)
    users_repo.assert_teacher_access(db_cursor, teacher_email, course_id)

    if users_repo.check_teacher_access(db_cursor, new_teacher_email, course_id):
        raise HTTPException(
            status_code=404,
            detail="User to invite already has teacher right at this course",
        )
    if users_repo.check_student_access(db_cursor, new_teacher_email, course_id):
        raise HTTPException(
            status_code=404, detail="Can't invite course student as a teacher"
        )
    if users_repo.check_parent_access(db_cursor, new_teacher_email, course_id):
        raise HTTPException(status_code=404, detail="Can't invite parent as a teacher")

    users_repo.add_teacher_to_course(db_cursor, db_conn, new_teacher_email, course_id)
    return {"success": True}


def remove_teacher_logic(
    db_cursor, db_conn, course_id, removing_teacher_email, teacher_email
):
    courses_repo.assert_course_exists(db_cursor, course_id)
    users_repo.assert_user_exists(db_cursor, removing_teacher_email)
    users_repo.assert_teacher_access(db_cursor, teacher_email, course_id)

    if not users_repo.check_teacher_access(
        db_cursor, removing_teacher_email, course_id
    ):
        raise HTTPException(
            status_code=404, detail="User to remove is not a teacher at this course"
        )

    teachers_left = users_repo.count_teachers_in_course(db_cursor, course_id)
    if teachers_left == 1:
        raise HTTPException(
            status_code=404, detail="Cannot remove the last teacher at the course"
        )

    users_repo.remove_teacher_from_course(
        db_cursor, db_conn, removing_teacher_email, course_id
    )
    return {"success": True}


def get_students_parents_logic(db_cursor, course_id, student_email, user_email):
    users_repo.assert_user_exists(db_cursor, student_email)
    courses_repo.assert_course_exists(db_cursor, course_id)
    users_repo.assert_teacher_access(db_cursor, user_email, course_id)

    if not users_repo.check_student_access(db_cursor, student_email, course_id):
        raise HTTPException(
            status_code=404, detail="Provided user in not a student at this course"
        )

    parents = users_repo.get_students_parents(db_cursor, course_id, student_email)
    return [{"email": par[0], "name": par[1]} for par in parents]


def get_course_teachers_logic(db_cursor, course_id, user_email):
    courses_repo.assert_course_exists(db_cursor, course_id)
    courses_repo.assert_course_access(db_cursor, user_email, course_id)

    teachers = users_repo.get_course_teachers(db_cursor, course_id)
    return [{"email": tch[0], "name": tch[1]} for tch in teachers]
