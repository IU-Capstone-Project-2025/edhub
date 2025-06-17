from fastapi import HTTPException
from constants import TIME_FORMAT
import constraints


def available_courses(db_cursor, user_email: str):
    # finding available courses
    db_cursor.execute(
        """
        SELECT courseid AS cid FROM teaches WHERE email = %s
        UNION
        SELECT courseid AS cid FROM student_at WHERE email = %s
        UNION
        SELECT courseid AS cid FROM parent_of_at_course WHERE parentemail = %s
    """,
        (user_email, user_email, user_email),
    )
    courses = db_cursor.fetchall()

    result = [{"course_id": crs[0]} for crs in courses]
    return result


def create_course(db_conn, db_cursor, title: str, user_email: str):

    # create course
    db_cursor.execute(
        "INSERT INTO courses (courseid, name, timecreated) VALUES (gen_random_uuid(), %s, now()) RETURNING courseid",
        (title,),
    )
    course_id = db_cursor.fetchone()[0]
    db_conn.commit()

    # add teacher
    db_cursor.execute(
        "INSERT INTO teaches (email, courseid) VALUES (%s, %s)", (user_email, course_id)
    )
    db_conn.commit()

    return {"course_id": course_id}


# WARNING: update if new elements appear
def remove_course(db_conn, db_cursor, course_id: str, user_email: str):

    constraints.assert_teacher_access(db_cursor, user_email, course_id)

    # remove course
    db_cursor.execute("DELETE FROM courses WHERE courseid = %s", (course_id,))
    db_conn.commit()

    return {"success": True}


def get_course_info(db_cursor, course_id: str, user_email: str):

    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # getting course info
    db_cursor.execute(
        """
        SELECT c.courseid, c.name, c.timecreated, COUNT(sa.email) AS student_count
        FROM courses c
        LEFT JOIN student_at sa ON c.courseid = sa.courseid
        WHERE c.courseid = %s
        GROUP BY c.courseid
    """,
        (course_id,),
    )
    course = db_cursor.fetchone()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    res = {
        "course_id": str(course[0]),
        "title": course[1],
        "creation_time": course[2].strftime(TIME_FORMAT),
        "number_of_students": course[3],
    }
    return res


def get_course_feed(db_cursor, course_id: str, user_email: str):

    # checking constraints
    constraints.assert_course_access(db_cursor, user_email, course_id)

    # finding course feed
    db_cursor.execute(
        """
        SELECT courseid AS cid, matid as postid, 'mat' as type, timeadded, author
        FROM course_materials
        WHERE courseid = %s

        UNION

        SELECT courseid AS cid, assid as postid, 'ass' as type, timeadded, author
        FROM course_assignments 
        WHERE courseid = %s

        ORDER BY timeadded DESC
    """,
        (course_id, course_id),
    )
    course_feed = db_cursor.fetchall()

    res = [
        {
            "course_id": str(mat[0]),
            "post_id": mat[1],
            "type": mat[2],
            "timeadded": mat[3].strftime(TIME_FORMAT),
            "author": mat[4],
        }
        for mat in course_feed
    ]

    return res
