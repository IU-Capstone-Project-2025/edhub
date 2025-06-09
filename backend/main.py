from fastapi import FastAPI, HTTPException, Depends
from auth import get_current_user, router as auth_router, get_db
from fastapi.middleware.cors import CORSMiddleware
import json_classes
from typing import List

app = FastAPI()
app.include_router(auth_router)

# TODO: прописать конкретные доверенные источники (на прод уже)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# checking whether the user exists in our LMS
def check_user_exists(db_cursor, user_email: str):
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (user_email,))
    user_exists = db_cursor.fetchone()[0]
    if not user_exists:
        raise HTTPException(status_code=404, detail="No user with provided email")
    return True


# checking whether the course exists in our LMS
def check_course_exists(db_cursor, course_id: str):
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM courses WHERE courseid = %s)", (course_id,))
    course_exists = db_cursor.fetchone()[0]
    if not course_exists:
        raise HTTPException(status_code=404, detail="No course with provided ID")
    return True


# checking whether the course exists in our LMS
def check_material_exists(db_cursor, course_id: str, material_id: str):
    try:
        material_id = int(material_id)
        check_course_exists(db_cursor, course_id)
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM course_materials WHERE courseid = %s AND matid = %s  )", (course_id, material_id))
        material_exists = db_cursor.fetchone()[0]
        if not material_exists:
            raise HTTPException(status_code=404, detail="No material with provided ID in this course")
        return True
    except Exception:
        raise HTTPException(status_code=404, detail="Material ID should be integer")


# checking whether the user has access to course in our LMS
def check_course_access(db_cursor, user_email: str, course_id: str, is_teacher: bool = False, is_student: bool = False, is_parent: bool = False):

    if is_teacher:
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM teaches WHERE email = %s AND courseid = %s)", (user_email, course_id))
        has_access = db_cursor.fetchone()[0]
        if not has_access:
            raise HTTPException(status_code=403, detail="User is not teacher at this course")
        return True

    elif is_student:
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM student_at WHERE email = %s AND courseid = %s)", (user_email, course_id))
        has_access = db_cursor.fetchone()[0]
        if not has_access:
            raise HTTPException(status_code=403, detail="User is not student at this course")
        return True

    elif is_parent:
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND courseid = %s)", (user_email, course_id))
        has_access = db_cursor.fetchone()[0]
        if not has_access:
            raise HTTPException(status_code=403, detail="User is not parent at this course")
        return True

    else:
        db_cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM teaches WHERE email = %s AND courseid = %s
                UNION
                SELECT 1 FROM student_at WHERE email = %s AND courseid = %s
                UNION
                SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND courseid = %s
            )
        """, (user_email, course_id, user_email, course_id, user_email, course_id))
        has_access = db_cursor.fetchone()[0]
        if not has_access:
            raise HTTPException(status_code=403, detail="User does not have access to this course")
        return True


@app.get('/available_courses', response_model=List[json_classes.CourseId])
async def available_courses(user_email: str = Depends(get_current_user)):

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

    with get_db() as (db_conn, db_cursor):
        check_course_exists(db_cursor, course_id)
        check_course_access(db_cursor=db_cursor, user_email=user_email, course_id=course_id, is_teacher=True)

    # connection to database
    with get_db() as (db_conn, db_cursor):

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

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_course_exists(db_cursor, course_id)
        check_course_access(db_cursor=db_cursor, user_email=user_email, course_id=course_id)

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
        "creation_date": course[2].strftime("%m-%d-%Y %H:%M:%S"),
        "number_of_students": course[3]
    }
    return res


@app.get('/get_course_feed', response_model=List[json_classes.MaterialID])
async def get_course_feed(course_id: str, user_email: str = Depends(get_current_user)):

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_course_exists(db_cursor, course_id)
        check_course_access(db_cursor=db_cursor, user_email=user_email, course_id=course_id)

        # finding course feed
        db_cursor.execute("SELECT courseid, matid FROM course_materials WHERE courseid = %s", (course_id,))
        course_feed = db_cursor.fetchall()

    res = [{'course_id': str(mat[0]), 'material_id': mat[1]} for mat in course_feed]
    return res


@app.post('/create_material', response_model=json_classes.MaterialID)
async def create_material(course_id: str, title: str, description: str, user_email: str = Depends(get_current_user)):

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_course_exists(db_cursor, course_id)
        check_course_access(db_cursor=db_cursor, user_email=user_email, course_id=course_id, is_teacher=True)

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

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_material_exists(db_cursor, course_id, material_id)
        check_course_access(db_cursor=db_cursor, user_email=user_email, course_id=course_id, is_teacher=True)

        # remove material
        db_cursor.execute("DELETE FROM course_materials WHERE courseid = %s AND matid = %s", (course_id, material_id))
        db_conn.commit()

    return {"success": True}


@app.get('/get_material', response_model=json_classes.Material)
async def get_material(course_id: str, material_id: str, user_email: str = Depends(get_current_user)):

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_course_exists(db_cursor, course_id)
        check_course_access(db_cursor=db_cursor, user_email=user_email, course_id=course_id)

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
        "creation_date": material[2].strftime("%m-%d-%Y %H:%M:%S"),
        "title": material[3],
        "description": material[4]
    }
    return res


@app.get('/get_enrolled_students', response_model=List[json_classes.User])
async def get_enrolled_students(course_id: str, user_email: str = Depends(get_current_user)):

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_course_exists(db_cursor, course_id)
        check_course_access(db_cursor=db_cursor, user_email=user_email, course_id=course_id)

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

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_course_exists(db_cursor, course_id)
        check_user_exists(db_cursor, student_email)
        check_course_access(db_cursor=db_cursor, user_email=teacher_email, course_id=course_id, is_teacher=True)

        # check if the student already enrolled to course
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM student_at WHERE email = %s AND courseid = %s)", (student_email, course_id))
        student_enrolled = db_cursor.fetchone()[0]
        if student_enrolled:
            raise HTTPException(status_code=404, detail="Student already enrolled at this course")

        # invite student
        db_cursor.execute(
            "INSERT INTO student_at (email, courseid) VALUES (%s, %s)",
            (student_email, course_id)
        )
        db_conn.commit()

    return {'success': True}


@app.post('/remove_student', response_model=json_classes.Success)
async def remove_student(course_id: str, student_email: str, teacher_email: str = Depends(get_current_user)):

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_course_exists(db_cursor, course_id)
        check_user_exists(db_cursor, student_email)
        check_course_access(db_cursor=db_cursor, user_email=teacher_email, course_id=course_id, is_teacher=True)

        # check if the student enrolled to course
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM student_at WHERE email = %s AND courseid = %s)", (student_email, course_id))
        student_enrolled = db_cursor.fetchone()[0]
        if not student_enrolled:
            raise HTTPException(status_code=404, detail="Student is not enrolled to this course")

        # remove student
        db_cursor.execute(
            "DELETE FROM student_at WHERE courseid = %s AND email = %s",
            (course_id, student_email)
        )
        db_conn.commit()

        # remove student's parents
        db_cursor.execute(
            "DELETE FROM parent_of_at_course WHERE courseid = %s AND studentemail = %s",
            (course_id, student_email)
        )
        db_conn.commit()

    return {"success": True}


@app.get('/get_students_parents', response_model=List[json_classes.User])
async def get_students_parents(course_id: str, student_email: str, user_email: str = Depends(get_current_user)):

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_user_exists(db_cursor, student_email)
        check_course_exists(db_cursor, course_id)
        check_course_access(db_cursor=db_cursor, user_email=user_email, course_id=course_id, is_teacher=True)

        # check if the student is enrolled to course
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM student_at WHERE email = %s AND courseid = %s)", (student_email, course_id))
        student_enrolled = db_cursor.fetchone()[0]
        if not student_enrolled:
            raise HTTPException(status_code=404, detail="Student is not enrolled to this course")

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

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_user_exists(db_cursor, student_email)
        check_user_exists(db_cursor, parent_email)
        check_course_exists(db_cursor, course_id)
        check_course_access(db_cursor=db_cursor, user_email=teacher_email, course_id=course_id, is_teacher=True)
        check_course_access(db_cursor=db_cursor, user_email=student_email, course_id=course_id, is_student=True)

        # check if the parent already assigned to the course with the student
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND studentemail = %s AND courseid = %s)", (parent_email, student_email, course_id))
        parent_assigned = db_cursor.fetchone()[0]
        if parent_assigned:
            raise HTTPException(status_code=404, detail="Parent already assigned to this student at this course")

        # invite parent
        db_cursor.execute(
            "INSERT INTO parent_of_at_course (parentemail, studentemail, courseid) VALUES (%s, %s, %s)",
            (parent_email, student_email, course_id)
        )
        db_conn.commit()

    return {'success': True}


@app.post('/remove_parent', response_model=json_classes.Success)
async def remove_parent(course_id: str, student_email: str, parent_email: str, teacher_email: str = Depends(get_current_user)):

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_course_exists(db_cursor, course_id)
        check_user_exists(db_cursor, student_email)
        check_user_exists(db_cursor, parent_email)
        check_course_access(db_cursor=db_cursor, user_email=teacher_email, course_id=course_id, is_teacher=True)

        # check if the parent assigned to the course with the student
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM parent_of_at_course WHERE parentemail = %s AND studentemail = %s AND courseid = %s)", (parent_email, student_email, course_id))
        parent_assigned = db_cursor.fetchone()[0]
        if not parent_assigned:
            raise HTTPException(status_code=404, detail="Parent is not assigned to this student at this course")

        # remove parent
        db_cursor.execute(
            "DELETE FROM parent_of_at_course WHERE courseid = %s AND studentemail = %s AND parentemail = %s",
            (course_id, student_email, parent_email)
        )
        db_conn.commit()

    return {"success": True}


@app.get('/get_course_teachers', response_model=List[json_classes.User])
async def get_course_teachers(course_id: str, user_email: str = Depends(get_current_user)):

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_course_exists(db_cursor, course_id)
        check_course_access(db_cursor=db_cursor, user_email=user_email, course_id=course_id)

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

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_course_exists(db_cursor, course_id)
        check_user_exists(db_cursor, new_teacher_email)
        check_course_access(db_cursor=db_cursor, user_email=teacher_email, course_id=course_id, is_teacher=True)

        # check if the teacher already assigned to course
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM teaches WHERE email = %s AND courseid = %s)", (new_teacher_email, course_id))
        teacher_assigned = db_cursor.fetchone()[0]
        if teacher_assigned:
            raise HTTPException(status_code=404, detail="Teacher already assigned to this course")

        # invite teacher
        db_cursor.execute(
            "INSERT INTO teaches (email, courseid) VALUES (%s, %s)",
            (new_teacher_email, course_id)
        )
        db_conn.commit()

    return {'success': True}


@app.post('/remove_teacher', response_model=json_classes.Success)
async def remove_teacher(course_id: str, removing_teacher_email: str, teacher_email: str = Depends(get_current_user)):

    # connection to database
    with get_db() as (db_conn, db_cursor):

        # checking constrants
        check_course_exists(db_cursor, course_id)
        check_user_exists(db_cursor, removing_teacher_email)
        check_course_access(db_cursor=db_cursor, user_email=teacher_email, course_id=course_id, is_teacher=True)

        # check if the teacher assigned to the course
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM teaches WHERE email = %s AND courseid = %s)", (removing_teacher_email, course_id))
        teacher_assigned = db_cursor.fetchone()[0]
        if not teacher_assigned:
            raise HTTPException(status_code=404, detail="Teacher is not assigned to this course")

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
