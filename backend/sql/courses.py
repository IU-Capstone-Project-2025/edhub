from typing import Union
from sql.dto import CourseInfoDTO, CourseFeedItemDTO


def select_available_courses(conn, user_email: str) -> list[str]:
    """
    Returns the list of all courses where the user is a teacher, a parent, or a student
    in no particular order.

    Note that the function ignores the admin status, if the user has it.
    """
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT courseid AS cid FROM teaches WHERE email = %s
            UNION
            SELECT courseid AS cid FROM student_at WHERE email = %s
            UNION
            SELECT DISTINCT courseid AS cid FROM parent_of_at_course WHERE parentemail = %s
            """,
            (user_email, user_email, user_email),
        )
        return db_cursor.fetchall()


def select_all_courses(conn) -> list[str]:
    with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT courseid FROM courses")
        return db_cursor.fetchall()[0]


def insert_course(conn, title: str) -> str:
    """
    Returns the new course ID.
    """
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "INSERT INTO courses (courseid, name, timecreated) VALUES (gen_random_uuid(), %s, now()) RETURNING courseid",
            (title,),
        )
        return db_cursor.fetchone()[0]


def delete_course(conn, course_id: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute("DELETE FROM courses WHERE courseid = %s", (course_id,))


def select_course_info(conn, course_id: str) -> CourseInfoDTO:
    with conn.cursor() as db_cursor:
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
        return CourseInfoDTO(db_cursor.fetchone())


def select_course_feed(conn, course_id: str) -> list[CourseFeedItemDTO]:
    """
    Returns the full list of course posts (currently materals and assignments), recent ones first.
    """
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT matid as postid, %s as type, timeadded, author
            FROM course_materials
            WHERE courseid = %s

            UNION

            SELECT assid as postid, %s as type, timeadded, author
            FROM course_assignments
            WHERE courseid = %s

            ORDER BY timeadded DESC
            """,
            (CourseFeedItemDTO.POST_MATERIAL, course_id, CourseFeedItemDTO.POST_ASSIGNMENT, course_id),
        )
        return [CourseFeedItemDTO(course_id, *attrs) for attrs in db_cursor.fetchall()]


def select_grades_in_course(conn, course_id: str,
                            students: Union[list[str], None] = None,
                            assignments: Union[list[int], None] = None) -> list[tuple[str, int, Union[int, None]]]:
    """
    Returns the list of grades in all submissions to the given assignments by the given students.
    These grades are represented as triplets: `(studentEmail, assignmentId, grade)`.

    Note that some submissions may be not graded, so `grade` can be `None`.

    If `students` is None, select all students.

    If `assignments` is None, select all assignments.
    """
    with conn.cursor() as db_cursor:
        if students is not None and len(students) == 0:
            return []
        if assignments is not None and len(assignments) == 0:
            return []
        query = "SELECT email, assid, grade FROM course_assignments_submissions WHERE courseid = %s"
        qargs = [course_id]
        if students is not None:
            query += " AND email in %s"
            qargs.append(tuple(students))
        if assignments is not None:
            query += " AND assid in %s"
            qargs.append(tuple(assignments))
        db_cursor.execute(query, tuple(qargs))
        return db_cursor.fetchall()
