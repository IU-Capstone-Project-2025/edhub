from sql.dto import AttachmentInfoDTO


def select_submission_grade(conn, course_id: str, assignment_id: int, student_email: str) -> Union[int, None]:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "SELECT grade FROM course_assignments_submissions WHERE courseid = %s AND assid = %s AND email = %s",
            (course_id, assignment_id, student_email),
        )
        return db_cursor.fetchone()[0]


def insert_submission(conn, course_id: str, assignment_id: int, student_email: str, comment: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """INSERT INTO course_assignments_submissions
            (courseid, assid, email, timeadded, timemodified, comment, grade, gradedby)
            VALUES (%s, %s, %s, now(), now(), %s, null, null)""",
            (course_id, assignment_id, student_email, comment),
        )


def insert_submission_attachment(system_conn, storage_conn, course_id: str, assignment_id: int,
                                 student_email: str, filename: str, contents: bytes) -> tuple[str, datetime]:
    """
    Returns the id of the new file and its upload time
    """
    with storage_conn.cursor() as storage_db_cursor:
        storage_db_cursor.execute(
            """
            INSERT INTO files
            (id, content)
            VALUES (gen_random_uuid(), %s)
            RETURNING id
            """,
            (contents, )
        )
        fileid = storage_db_cursor.fetchone()[0]

    with system_conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            INSERT INTO submissions_files
            (courseid, assid, email, fileid, filename, uploadtime)
            VALUES (%s, %s, %s, %s, %s, now())
            RETURNING fileid, uploadtime
            """,
            (course_id, assignment_id, student_email, fileid, filename),
        )
        return db_cursor.fetchone()


def select_submission_attachments(conn, course_id: str, assignment_id: int, student_email: str) -> list[AttachmentInfoDTO]:
    with conn.cursor() as db_cursor:
    db_cursor.execute(
        """
        SELECT fileid, filename, uploadtime
        FROM submissions_files
        WHERE courseid = %s AND assid = %s AND email = %s
        """,
        (course_id, assignment_id, student_email),
    )
    return db_cursor.fetchall()


def update_submission_comment(conn, comment, course_id, assignment_id, student_email):
    with conn.cursor() as db_cursor:
    db_cursor.execute(
        """
        UPDATE course_assignments_submissions
        SET comment = %s, timemodified = now()
        WHERE courseid = %s AND assid = %s AND email = %s
        """,
        (comment, course_id, assignment_id, student_email),
    )


def select_submissions(conn, course_id, assignment_id):
    with conn.cursor() as db_cursor:
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
    return db_cursor.fetchall()


def select_single_submission(conn, course_id, assignment_id, student_email):
    with conn.cursor() as db_cursor:
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
    return db_cursor.fetchone()


def update_submission_grade(conn, grade, user_email, course_id, assignment_id, student_email):
    with conn.cursor() as db_cursor:
    db_cursor.execute(
        """
        UPDATE course_assignments_submissions
        SET grade = %s, gradedby = %s
        WHERE courseid = %s AND assid = %s AND email = %s
        """,
        (grade, user_email, course_id, assignment_id, student_email),
    )
