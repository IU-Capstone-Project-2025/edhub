from fastapi import FastAPI, HTTPException, Depends
from auth import get_current_user, router as auth_router, get_db
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json_classes
import constraints

app = FastAPI()
app.include_router(auth_router)
TIME_FORMAT = "%m-%d-%Y %H:%M:%S"

# TODO: прописать конкретные доверенные источники (на прод уже)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/available_courses', response_model=List[json_classes.CourseId])
async def available_courses(user_email: str = Depends(get_current_user)):
    '''
    Get the list of IDs of courses available for user (as a teacher, student, or parent).
    '''

    # finding available courses
    with get_db() as (db_conn, db_cursor):
        db_cursor.execute("""
            SELECT courseid AS cid FROM teaches WHERE email = %s
            UNION
            SELECT courseid AS cid FROM student_at WHERE email = %s
            UNION
            SELECT courseid AS cid FROM parent_of_at_course WHERE parentemail = %s
        """, (user_email, user_email, user_email))
        courses = db_cursor.fetchall()

    result = [{'course_id': crs[0]} for crs in courses]
    return result


@app.post('/create_course', response_model=json_classes.CourseId)
async def create_course(title: str, user_email: str = Depends(get_current_user)):
    '''
    Create the course with provided title and become a teacher in it.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # create course
        db_cursor.execute("INSERT INTO courses (courseid, name, timecreated) VALUES (gen_random_uuid(), %s, now()) RETURNING courseid", (title,))
        course_id = db_cursor.fetchone()[0]
        db_conn.commit()

        # add teacher
        db_cursor.execute("INSERT INTO teaches (email, courseid) VALUES (%s, %s)", (user_email, course_id))
        db_conn.commit()

    return {"course_id": course_id}


@app.post('/remove_course', response_model=json_classes.Success)
async def remove_course(course_id: str, user_email: str = Depends(get_current_user)):
    '''
    Remove the course with provided course_id.

    All the course materials, teachers, students, and parents will be also removed.

    Teacher role required.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        # remove course
        db_cursor.execute("DELETE FROM courses WHERE courseid = %s", (course_id, ))
        db_conn.commit()

        # remove materials
        db_cursor.execute("DELETE FROM course_materials WHERE courseid = %s", (course_id, ))
        db_conn.commit()

        # remove teachers
        db_cursor.execute("DELETE FROM teaches WHERE courseid = %s", (course_id, ))
        db_conn.commit()

        # remove students
        db_cursor.execute("DELETE FROM student_at WHERE courseid = %s", (course_id, ))
        db_conn.commit()

        # remove parents
        db_cursor.execute("DELETE FROM parent_of_at_course WHERE courseid = %s", (course_id, ))
        db_conn.commit()

    return {"success": True}


@app.get('/get_course_info', response_model=json_classes.Course)
async def get_course_info(course_id: str, user_email: str = Depends(get_current_user)):
    f'''
    Get information about the course: course_id, title, creation date, and number of enrolled students.

    The format of creation time is "{TIME_FORMAT}".
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_access(db_cursor, user_email, course_id)

        # getting course info
        db_cursor.execute("""
            SELECT c.courseid, c.name, c.timecreated, COUNT(sa.email) AS student_count
            FROM courses c
            LEFT JOIN student_at sa ON c.courseid = sa.courseid
            WHERE c.courseid = %s
            GROUP BY c.courseid
        """, (course_id,))
        course = db_cursor.fetchone()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

    res = {
        "course_id": str(course[0]),
        "title": course[1],
        "creation_time": course[2].strftime(TIME_FORMAT),
        "number_of_students": course[3]
    }
    return res


@app.get('/get_course_feed', response_model=List[json_classes.CoursePost])
async def get_course_feed(course_id: str, user_email: str = Depends(get_current_user)):
    '''
    Get the course feed with all its materials.

    Materials are ordered by creation_date, the first posts are new.

    Returns the list of (course_id, post_id, type) for each material.

    Type can be 'mat' for material and 'ass' for assignment.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_access(db_cursor, user_email, course_id)

        # finding course feed
        db_cursor.execute("""
            SELECT courseid AS cid, matid as postid, 'mat' as type, timeadded
            FROM course_materials
            WHERE courseid = %s

            UNION

            SELECT courseid AS cid, assid as postid, 'ass' as type, timeadded 
            FROM course_assignments 
            WHERE courseid = %s

            ORDER BY timeadded DESC
        """, (course_id, course_id))
        course_feed = db_cursor.fetchall()

    res = [{'course_id': str(mat[0]), 'post_id': mat[1], 'type': mat[2]} for mat in course_feed]
    return res


@app.post('/create_material', response_model=json_classes.MaterialID)
async def create_material(course_id: str, title: str, description: str, user_email: str = Depends(get_current_user)):
    '''
    Create the material with provided title and description in the course with provided course_id.

    Teacher role required.

    Returns the (course_id, material_id) for the new material in case of success.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        # create material
        db_cursor.execute(
            "INSERT INTO course_materials (courseid, name, description, timeadded) VALUES (%s, %s, %s, now()) RETURNING matid",
            (course_id, title, description)
        )
        material_id = db_cursor.fetchone()[0]
        db_conn.commit()

    return {"course_id": course_id, "material_id": material_id}


@app.post('/remove_material', response_model=json_classes.Success)
async def remove_material(course_id: str, material_id: str, user_email: str = Depends(get_current_user)):
    '''
    Remove the material by the provided course_id and material_id.

    Teacher role required.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_material_exists(db_cursor, course_id, material_id)
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        # remove material
        db_cursor.execute("DELETE FROM course_materials WHERE courseid = %s AND matid = %s", (course_id, material_id))
        db_conn.commit()

    return {"success": True}


@app.get('/get_material', response_model=json_classes.Material)
async def get_material(course_id: str, material_id: str, user_email: str = Depends(get_current_user)):
    f'''
    Get the material details by the provided (course_id, material_id).

    Returns course_id, material_id, creation_time, title, and description.

    The format of creation time is "{TIME_FORMAT}".
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_access(db_cursor, user_email, course_id)

        # searching for materials
        db_cursor.execute("""
            SELECT courseid, matid, timeadded, name, description
            FROM course_materials
            WHERE courseid = %s AND matid = %s
        """, (course_id, material_id))
        material = db_cursor.fetchone()
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")

    res = {
        "course_id": str(material[0]),
        "material_id": material[1],
        "creation_time": material[2].strftime(TIME_FORMAT),
        "title": material[3],
        "description": material[4]
    }
    return res


@app.post('/create_assignment', response_model=json_classes.AssignmentID)
async def create_assignment(course_id: str, title: str, description: str, user_email: str = Depends(get_current_user)):
    '''
    Create the assignment with provided title and description in the course with provided course_id.

    Teacher role required.

    Returns the (course_id, assignment_id) for the new material in case of success.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        # create material
        db_cursor.execute(
            "INSERT INTO course_assignments (courseid, name, description, timeadded) VALUES (%s, %s, %s, now()) RETURNING assid",
            (course_id, title, description)
        )
        assignment_id = db_cursor.fetchone()[0]
        db_conn.commit()

    return {"course_id": course_id, "assignment_id": assignment_id}


@app.post('/remove_assignment', response_model=json_classes.Success)
async def remove_assignment(course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)):
    '''
    Remove the assignment by the provided course_id and assignment_id.

    Teacher role required.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        # remove material
        db_cursor.execute("DELETE FROM course_assignments WHERE courseid = %s AND assid = %s", (course_id, assignment_id))
        db_conn.commit()

        # remove students' submissions
        db_cursor.execute("DELETE FROM course_assignments_submissions WHERE courseid = %s AND assid = %s", (course_id, assignment_id))
        db_conn.commit()

    return {"success": True}


@app.get('/get_assignment', response_model=json_classes.Assignment)
async def get_assignment(course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)):
    f'''
    Get the assignment details by the provided (course_id, assignment_id).

    Returns course_id, assignment_id, creation_time, title, and description.

    The format of creation time is "{TIME_FORMAT}".
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_access(db_cursor, user_email, course_id)

        # searching for assignments
        db_cursor.execute("""
            SELECT courseid, assid, timeadded, name, description
            FROM course_assignments
            WHERE courseid = %s AND assid = %s
        """, (course_id, assignment_id))
        assignment = db_cursor.fetchone()
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")

    res = {
        "course_id": str(assignment[0]),
        "assignment_id": assignment[1],
        "creation_time": assignment[2].strftime(TIME_FORMAT),
        "title": assignment[3],
        "description": assignment[4]
    }
    return res


@app.get('/get_enrolled_students', response_model=List[json_classes.User])
async def get_enrolled_students(course_id: str, user_email: str = Depends(get_current_user)):
    '''
    Get the list of enrolled students by course_id.

    Return the email and name of the student.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_access(db_cursor, user_email, course_id)

        # finding enrolled students
        db_cursor.execute("""
            SELECT
                s.email,
                u.publicname
            FROM student_at s
            JOIN users u ON s.email = u.email
            WHERE s.courseid = %s
        """, (course_id,))
        students = db_cursor.fetchall()

    res = [{'email': st[0], 'name': st[1]} for st in students]
    return res


@app.post('/invite_student', response_model=json_classes.Success)
async def invite_student(course_id: str, student_email: str, teacher_email: str = Depends(get_current_user)):
    '''
    Add the student with provided email to the course with provided course_id.

    Teacher role required.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_user_exists(db_cursor, student_email)
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

        # check if the student already enrolled to course
        if constraints.check_student_access(db_cursor, student_email, course_id):
            raise HTTPException(status_code=403, detail="The invited user already has student rights in this course")

        # check if the potential student already has teacher rights at this course
        if constraints.check_teacher_access(db_cursor, student_email, course_id):
            raise HTTPException(status_code=403, detail="Can't invite course teacher as a student")

        # check if the potential student already has parent rights at this course
        if constraints.check_parent_access(db_cursor, student_email, course_id):
            raise HTTPException(status_code=403, detail="Can't invite parent as a student")

        # invite student
        db_cursor.execute(
            "INSERT INTO student_at (email, courseid) VALUES (%s, %s)",
            (student_email, course_id)
        )
        db_conn.commit()

    return {'success': True}


@app.post('/remove_student', response_model=json_classes.Success)
async def remove_student(course_id: str, student_email: str, teacher_email: str = Depends(get_current_user)):
    '''
    Remove the student with provided email from the course with provided course_id.

    Teacher role required.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

        # check if the student is enrolled to course
        constraints.assert_student_access(db_cursor, student_email, course_id)

        # remove student
        db_cursor.execute(
            "DELETE FROM student_at WHERE courseid = %s AND email = %s",
            (course_id, student_email)
        )

        # remove student's parents
        db_cursor.execute(
            "DELETE FROM parent_of_at_course WHERE courseid = %s AND studentemail = %s",
            (course_id, student_email)
        )
        db_conn.commit()

    return {"success": True}


@app.get('/get_students_parents', response_model=List[json_classes.User])
async def get_students_parents(course_id: str, student_email: str, user_email: str = Depends(get_current_user)):
    '''
    Get the list of parents observing the student with provided email on course with provided course_id.

    Teacher role required.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        # check if the student is enrolled to course
        constraints.assert_student_access(db_cursor, student_email, course_id)

        # finding student's parents
        db_cursor.execute("""
            SELECT
                p.parentemail,
                u.publicname
            FROM parent_of_at_course p
            JOIN users u ON p.parentemail = u.email
            WHERE p.courseid = %s AND p.studentemail = %s
        """, (course_id, student_email))
        parents = db_cursor.fetchall()

    res = [{'email': par[0], 'name': par[1]} for par in parents]
    return res


@app.post('/invite_parent', response_model=json_classes.Success)
async def invite_parent(course_id: str, student_email: str, parent_email: str, teacher_email: str = Depends(get_current_user)):
    '''
    Invite the user with provided parent_email to become a parent of the student with provided student_email on course with provided course_id.

    Teacher role required.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

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
        db_cursor.execute(
            "INSERT INTO parent_of_at_course (parentemail, studentemail, courseid) VALUES (%s, %s, %s)",
            (parent_email, student_email, course_id)
        )
        db_conn.commit()

    return {'success': True}


@app.post('/remove_parent', response_model=json_classes.Success)
async def remove_parent(course_id: str, student_email: str, parent_email: str, teacher_email: str = Depends(get_current_user)):
    '''
    Remove the parent identified by parent_email from the tracking of student with provided student_email on course with provided course_id.

    Teacher role required.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

        # check if the parent assigned to the course with the student
        constraints.assert_parent_student_access(db_cursor, parent_email, student_email, course_id)

        # remove parent
        db_cursor.execute(
            "DELETE FROM parent_of_at_course WHERE courseid = %s AND studentemail = %s AND parentemail = %s",
            (course_id, student_email, parent_email)
        )
        db_conn.commit()

    return {"success": True}


@app.get('/get_parents_children', response_model=List[json_classes.User])
async def get_parents_children(course_id: str, user_email: str = Depends(get_current_user)):
    '''
    Get the list of students for the parent with provided email on course with provided course_id.

    Parent role required.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_exists(db_cursor, course_id)

        db_cursor.execute("""
            SELECT
                p.studentemail,
                u.publicname
            FROM parent_of_at_course p
            JOIN users u ON p.studentemail = u.email
            WHERE p.courseid = %s AND p.parentemail = %s
        """, (course_id, user_email))
        parents = db_cursor.fetchall()

    res = [{'email': par[0], 'name': par[1]} for par in parents]
    return res


@app.get('/get_course_teachers', response_model=List[json_classes.User])
async def get_course_teachers(course_id: str, user_email: str = Depends(get_current_user)):
    '''
    Get the list of teachers teaching the course with the provided course_id.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_course_access(db_cursor, user_email, course_id)

        # finding assigned teachers
        db_cursor.execute("""
            SELECT
                t.email,
                u.publicname
            FROM teaches t
            JOIN users u ON t.email = u.email
            WHERE t.courseid = %s
            GROUP BY t.email, u.publicname
        """, (course_id,))
        teachers = db_cursor.fetchall()

    res = [{'email': tch[0], 'name': tch[1]} for tch in teachers]
    return res


@app.post('/invite_teacher', response_model=json_classes.Success)
async def invite_teacher(course_id: str, new_teacher_email: str, teacher_email: str = Depends(get_current_user)):
    '''
    Add the user with provided new_teacher_email as a techer to the course with provided course_id.

    Teacher role required.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_user_exists(db_cursor, new_teacher_email)
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

        # check if the teacher already assigned to course
        if constraints.check_teacher_access(db_cursor, new_teacher_email, course_id):
            raise HTTPException(status_code=403, detail="User to invite already has teacher right at this course")

        # check if the potential teacher already has student rights at this course
        if constraints.check_student_access(db_cursor, new_teacher_email, course_id):
            raise HTTPException(status_code=403, detail="Can't invite course student as a teacher")

        # check if the potential teacher already has parent rights at this course
        if constraints.check_parent_access(db_cursor, new_teacher_email, course_id):
            raise HTTPException(status_code=403, detail="Can't invite parent as a teacher")

        # invite teacher
        db_cursor.execute(
            "INSERT INTO teaches (email, courseid) VALUES (%s, %s)",
            (new_teacher_email, course_id)
        )
        db_conn.commit()

    return {'success': True}


@app.post('/remove_teacher', response_model=json_classes.Success)
async def remove_teacher(course_id: str, removing_teacher_email: str, teacher_email: str = Depends(get_current_user)):
    '''
    Remove the teacher with removing_teacher_email from the course with provided course_id.

    Teacher role required.

    Teacher can remove themself.

    At least one teacher should stay in the course.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_user_exists(db_cursor, removing_teacher_email)
        constraints.assert_teacher_access(db_cursor, teacher_email, course_id)

        # check if the teacher assigned to the course
        if not constraints.check_teacher_access(db_cursor, removing_teacher_email, course_id):
            raise HTTPException(status_code=403, detail="User to remove is not a teacher at this course")

        # ensuring that at least one teacher remains in the course
        db_cursor.execute("SELECT COUNT(*) FROM teaches WHERE courseid = %s", (course_id, ))
        teachers_left = db_cursor.fetchone()[0]
        if teachers_left == 1:
            raise HTTPException(status_code=404, detail="Cannot remove the last teacher at the course")

        # remove teacher
        db_cursor.execute(
            "DELETE FROM teaches WHERE courseid = %s AND email = %s",
            (course_id, removing_teacher_email)
        )
        db_conn.commit()

    return {"success": True}


@app.post('/submit_assignment', response_model=json_classes.Success)
async def submit_assignment(course_id: str, assignment_id: str, comment: str, student_email: str = Depends(get_current_user)):
    '''
    Allows student to submit their assignment.

    Student role required.

    Student cannot submit already graded assignment.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
        constraints.assert_student_access(db_cursor, student_email, course_id)

        db_cursor.execute("SELECT grade FROM course_assignments_submissions WHERE courseid = %s AND assid = %s AND email = %s", (course_id, assignment_id, student_email))
        submission = db_cursor.fetchone()

        # inserting submission
        if submission is None:
            db_cursor.execute(
                "INSERT INTO course_assignments_submissions (courseid, assid, email, timeadded, timemodified, comment, grade, gradedby) VALUES (%s, %s, %s, now(), now(), %s, null, null)",
                (course_id, assignment_id, student_email, comment)
            )
            db_conn.commit()

        # updating submission if not graded
        elif submission and submission[0] in (None, 'null'):
            db_cursor.execute("""
                UPDATE course_assignments_submissions
                SET comment = %s, timemodified = now()
                WHERE courseid = %s AND assid = %s AND email = %s
            """, (comment, course_id, assignment_id, student_email))
            db_conn.commit()

        else:
            raise HTTPException(status_code=404, detail="Can't edit the submission after it was graded.")

    return {"success": True}


@app.get('/get_assignment_submissions', response_model=List[json_classes.Submission])
async def get_assignment_submissions(course_id: str, assignment_id: str, user_email: str = Depends(get_current_user)):
    f'''
    Get the list of students submissions of provided assignments.

    Teacher role required.

    Submissions are ordered by submission_time, the first submissions are new.

    Returns the list of submissions (course_id, assignment_id, student_email, student_name, submission_time, last_modification_time, comment, grade, gradedby_email).

    The format of submission_time and last_modification_time is "{TIME_FORMAT}".

    `grade` and `gradedby_email` can be `null` if the assignment was not graded yet.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        # finding students' submissions
        db_cursor.execute("""
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
        """, (course_id, assignment_id))
        submissions = db_cursor.fetchall()

    res = [{'course_id': course_id,
            'assignment_id': assignment_id,
            'student_email': sub[0],
            'student_name': sub[1],
            'submission_time': sub[2].strftime(TIME_FORMAT),
            'last_modification_time': sub[3].strftime(TIME_FORMAT),
            'comment': sub[4],
            'grade': sub[5],
            'gradedby_email': sub[6]} for sub in submissions]
    return res


@app.get('/get_submission', response_model=json_classes.Submission)
async def get_submission(course_id: str, assignment_id: str, student_email: str, user_email: str = Depends(get_current_user)):
    f'''
    Get the student submission of assignment by course_id, assignment_id and student_email.

    - Teacher can get all submissions of the course
    - Parent can get the submission of their student
    - Stuent can get their submissions

    Returns the submission (course_id, assignment_id, student_email, student_name, submission_time, last_modification_time, comment, grade, gradedby_email).

    The format of submission_time and last_modification_time is "{TIME_FORMAT}".

    `grade` and `gradedby_email` can be `null` if the assignment was not graded yet.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
        constraints.assert_student_access(db_cursor, student_email, course_id)
        if not constraints.check_teacher_access(db_cursor, user_email, course_id) and not constraints.check_parent_student_access(db_cursor, user_email, student_email, course_id) and not student_email == user_email:
            raise HTTPException(status_code=403, detail="User does not have access to this submission")

        # finding student's submission
        db_cursor.execute("""
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
        """, (course_id, assignment_id, student_email))
        submission = db_cursor.fetchone()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission of this user is not found")
        submission = submission[0]

    res = {'course_id': course_id,
            'assignment_id': assignment_id,
            'student_email': submission[0],
            'student_name': submission[1],
            'submission_time': submission[2].strftime(TIME_FORMAT),
            'last_modification_time': submission[3].strftime(TIME_FORMAT),
            'comment': submission[4],
            'grade': submission[5],
            'gradedby_email': submission[6]}
    return res


@app.post('/grade_submission', response_model=json_classes.Success)
async def grade_submission(course_id: str, assignment_id: str, student_email: str, grade: str, user_email: str = Depends(get_current_user)):
    '''
    Allows teacher to grade student's submission.

    Teacher role required.
    '''

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constraints
        constraints.assert_assignment_exists(db_cursor, course_id, assignment_id)
        constraints.assert_teacher_access(db_cursor, user_email, course_id)

        # check if the student is enrolled to course
        if not constraints.check_student_access(db_cursor, student_email, course_id):
            raise HTTPException(status_code=403, detail="Provided user in not a student at this course")

        # check submission of student exists
        constraints.assert_submission_exists(db_cursor, course_id, assignment_id, student_email)

        # grading submission
        db_cursor.execute("""
            UPDATE course_assignments_submissions
            SET grade = %s, gradedby = %s
            WHERE courseid = %s AND assid = %s AND email = %s
        """, (grade, user_email, course_id, assignment_id, student_email))
        db_conn.commit()

    return {"success": True}
