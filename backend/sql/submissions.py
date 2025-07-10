def sql_select_submission_grade(db_cursor, course_id, assignment_id, student_email):
    db_cursor.execute(
        "SELECT grade FROM course_assignments_submissions WHERE courseid = %s AND assid = %s AND email = %s",
        (course_id, assignment_id, student_email),
    )
    return db_cursor.fetchone()


def sql_insert_submission(db_cursor, course_id, assignment_id, student_email, comment):
    db_cursor.execute(
        "INSERT INTO course_assignments_submissions (courseid, assid, email, timeadded, timemodified, comment, grade, gradedby) VALUES (%s, %s, %s, now(), now(), %s, null, null)",
        (course_id, assignment_id, student_email, comment),
    )


def sql_insert_submission_attachment(db_cursor, storage_db_cursor, course_id, assignment_id, student_email, filename, contents):
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


def sql_select_submission_attachments(db_cursor, course_id, assignment_id, student_email):
    db_cursor.execute(
        """
        SELECT fileid, filename, uploadtime
        FROM submissions_files
        WHERE courseid = %s AND assid = %s AND email = %s
        """,
        (course_id, assignment_id, student_email),
    )
    return db_cursor.fetchall()


def sql_update_submission_comment(db_cursor, comment, course_id, assignment_id, student_email):
    db_cursor.execute(
        """
        UPDATE course_assignments_submissions
        SET comment = %s, timemodified = now()
        WHERE courseid = %s AND assid = %s AND email = %s
        """,
        (comment, course_id, assignment_id, student_email),
    )


def sql_select_submissions(db_cursor, course_id, assignment_id):
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


def sql_select_single_submission(db_cursor, course_id, assignment_id, student_email):
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


def sql_update_submission_grade(db_cursor, grade, user_email, course_id, assignment_id, student_email):
    db_cursor.execute(
        """
        UPDATE course_assignments_submissions
        SET grade = %s, gradedby = %s
        WHERE courseid = %s AND assid = %s AND email = %s
        """,
        (grade, user_email, course_id, assignment_id, student_email),
    )
