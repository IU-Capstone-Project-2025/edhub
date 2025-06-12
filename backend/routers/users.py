from typing import List
from routers.auth import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException
import models.api, constraints
from routers.auth import get_current_user, get_db

router = APIRouter()


@router.get("/get_enrolled_students", response_model=List[models.api.User])
async def get_enrolled_students(
    course_id: str, user_email: str = Depends(get_current_user)
):
    """
    Get the list of enrolled stu    dents by course_id.

    Return the email and name of the student.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_exists(db_cursor, course_id)
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


@router.post("/invite_student", response_model=models.api.Success)
async def invite_student(
    course_id: str, student_email: str, teacher_email: str = Depends(get_current_user)
):
    """
    Add the student with provided email to the course with provided course_id.

    Teacher role required.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_exists(db_cursor, course_id)
        constraints.assert_user_exists(db_cursor, student_email)
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

        # check if the student already enrolled to course
        if constraints.check_student_access(db_cursor, student_email, course_id):
            raise HTTPException(
                status_code=404,
                detail="User to invite already has student right at this course",
            )

        # check if the potential student already has teacher rights at this course
        if constraints.check_teacher_access(db_cursor, student_email, course_id):
            raise HTTPException(
                status_code=404, detail="Can't invite course teacher as a student"
            )

        # check if the potential student already has parent rights at this course
        if constraints.check_parent_access(db_cursor, student_email, course_id):
            raise HTTPException(
                status_code=404, detail="Can't invite parent as a student"
            )

        # invite student
        db_cursor.execute(
            "INSERT INTO student_at (email, courseid) VALUES (%s, %s)",
            (student_email, course_id),
        )
        db_conn.commit()

    return {"success": True}


@router.post("/remove_student", response_model=models.api.Success)
async def remove_student(
    course_id: str, student_email: str, teacher_email: str = Depends(get_current_user)
):
    """
    Remove the student with provided email from the course with provided course_id.

    Teacher role required.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_exists(db_cursor, course_id)
        constraints.assert_user_exists(db_cursor, student_email)
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

        # check if the student enrolled to course
        if not constraints.check_student_access(db_cursor, student_email, course_id):
            raise HTTPException(
                status_code=404, detail="User to remove is not a student at this course"
            )

        # remove student
        db_cursor.execute(
            "DELETE FROM student_at WHERE courseid = %s AND email = %s",
            (course_id, student_email),
        )
        db_conn.commit()

        # remove student's parents
        db_cursor.execute(
            "DELETE FROM parent_of_at_course WHERE courseid = %s AND studentemail = %s",
            (course_id, student_email),
        )
        db_conn.commit()

    return {"success": True}


@router.get("/get_students_parents", response_model=List[models.api.User])
async def get_students_parents(
    course_id: str, student_email: str, user_email: str = Depends(get_current_user)
):
    """
    Get the list of parents observing the student with provided email on course with provided course_id.

    Teacher role required.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_user_exists(db_cursor, student_email)
        constraints.assert_course_exists(db_cursor, course_id)
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


@router.post("/invite_parent", response_model=models.api.Success)
async def invite_parent(
    course_id: str,
    student_email: str,
    parent_email: str,
    teacher_email: str = Depends(get_current_user),
):
    """
    Invite the user with provided parent_email to become a parent of the student with provided student_email on course with provided course_id.

    Teacher role required.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_user_exists(db_cursor, student_email)
        constraints.assert_user_exists(db_cursor, parent_email)
        constraints.assert_course_exists(db_cursor, course_id)
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)
        constraints.assert_student_access(db_cursor, student_email, course_id)

        # check if the parent already assigned to the course with the student
        if constraints.check_parent_student_access(
            db_cursor, parent_email, student_email, course_id
        ):
            raise HTTPException(
                status_code=404,
                detail="Parent already assigned to this student at this course",
            )

        # check if the potential parent already has teacher rights at this course
        if constraints.check_teacher_access(db_cursor, parent_email, course_id):
            raise HTTPException(
                status_code=404, detail="Can't invite course teacher as a parent"
            )

        # check if the potential parent already has student rights at this course
        if constraints.check_student_access(db_cursor, parent_email, course_id):
            raise HTTPException(
                status_code=404, detail="Can't invite course student as a parent"
            )

        # invite parent
        db_cursor.execute(
            "INSERT INTO parent_of_at_course (parentemail, studentemail, courseid) VALUES (%s, %s, %s)",
            (parent_email, student_email, course_id),
        )
        db_conn.commit()

    return {"success": True}


@router.post("/remove_parent", response_model=models.api.Success)
async def remove_parent(
    course_id: str,
    student_email: str,
    parent_email: str,
    teacher_email: str = Depends(get_current_user),
):
    """
    Remove the parent identified by parent_email from the tracking of student with provided student_email on course with provided course_id.

    Teacher role required.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_exists(db_cursor, course_id)
        constraints.assert_user_exists(db_cursor, student_email)
        constraints.assert_user_exists(db_cursor, parent_email)
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

        # check if the parent assigned to the course with the student
        if not constraints.check_parent_student_access(
            db_cursor, parent_email, student_email, course_id
        ):
            raise HTTPException(
                status_code=404,
                detail="Parent is not assigned to this student at this course",
            )

        # remove parent
        db_cursor.execute(
            "DELETE FROM parent_of_at_course WHERE courseid = %s AND studentemail = %s AND parentemail = %s",
            (course_id, student_email, parent_email),
        )
        db_conn.commit()

    return {"success": True}


@router.get("/get_course_teachers", response_model=List[models.api.User])
async def get_course_teachers(
    course_id: str, user_email: str = Depends(get_current_user)
):
    """
    Get the list of teachers teaching the course with the provided course_id.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_exists(db_cursor, course_id)
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


@router.post("/invite_teacher", response_model=models.api.Success)
async def invite_teacher(
    course_id: str,
    new_teacher_email: str,
    teacher_email: str = Depends(get_current_user),
):
    """
    Add the user with provided new_teacher_email as a techer to the course with provided course_id.

    Teacher role required.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_exists(db_cursor, course_id)
        constraints.assert_user_exists(db_cursor, new_teacher_email)
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

        # check if the teacher already assigned to course
        if constraints.check_teacher_access(db_cursor, new_teacher_email, course_id):
            raise HTTPException(
                status_code=404,
                detail="User to invite already has teacher right at this course",
            )

        # check if the potential teacher already has student rights at this course
        if constraints.check_student_access(db_cursor, new_teacher_email, course_id):
            raise HTTPException(
                status_code=404, detail="Can't invite course student as a teacher"
            )

        # check if the potential teacher already has parent rights at this course
        if constraints.check_parent_access(db_cursor, new_teacher_email, course_id):
            raise HTTPException(
                status_code=404, detail="Can't invite parent as a teacher"
            )

        # invite teacher
        db_cursor.execute(
            "INSERT INTO teaches (email, courseid) VALUES (%s, %s)",
            (new_teacher_email, course_id),
        )
        db_conn.commit()

    return {"success": True}


@router.post("/remove_teacher", response_model=models.api.Success)
async def remove_teacher(
    course_id: str,
    removing_teacher_email: str,
    teacher_email: str = Depends(get_current_user),
):
    """
    Remove the teacher with removing_teacher_email from the course with provided course_id.

    Teacher role required.

    Teacher can remove themself.

    At least one teacher should stay in the course.
    """

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_exists(db_cursor, course_id)
        constraints.assert_user_exists(db_cursor, removing_teacher_email)
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

        # check if the teacher assigned to the course
        if not constraints.check_teacher_access(
            db_cursor, removing_teacher_email, course_id
        ):
            raise HTTPException(
                status_code=404, detail="User to remove is not a teacher at this course"
            )

        # ensuring that at least one teacher remains in the course
        db_cursor.execute(
            "SELECT COUNT(*) FROM teaches WHERE courseid = %s", (course_id,)
        )
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
