def sql_insert_assignment(db_cursor, course_id, title, description, user_email):
    db_cursor.execute(
        "INSERT INTO course_assignments (courseid, name, description, timeadded, author) VALUES (%s, %s, %s, now(), %s) RETURNING assid",
        (course_id, title, description, user_email),
    )
    return db_cursor.fetchone()[0]


def sql_delete_assignment(db_cursor, course_id, assignment_id):
    db_cursor.execute(
        "DELETE FROM course_assignments WHERE courseid = %s AND assid = %s",
        (course_id, assignment_id),
    )


def sql_select_assignment(db_cursor, course_id, assignment_id):
    db_cursor.execute(
        """
        SELECT courseid, assid, timeadded, name, description, author
        FROM course_assignments
        WHERE courseid = %s AND assid = %s
        """,
        (course_id, assignment_id),
    )
    return db_cursor.fetchone()


def sql_insert_assignment_attachment(db_cursor, course_id, assignment_id, filename, contents):
    db_cursor.execute(
        """
        INSERT INTO assignment_files 
        (courseid, matid, filename, file, upload_time)
        VALUES (%s, %s, %s, %s, now())
        RETURNING fileid, upload_time
        """,
        (course_id, assignment_id, filename, contents),
    )
    return db_cursor.fetchone()


def sql_select_assignment_attachments(db_cursor, course_id, assignment_id):
    db_cursor.execute(
        """
        SELECT fileid, filename, upload_time
        FROM assignment_files
        WHERE courseid = %s AND matid = %s
        """,
        (course_id, assignment_id),
    )
    return db_cursor.fetchall()


def sql_download_assignment_attachment(db_cursor, course_id, assignment_id, file_id):
    db_cursor.execute(
        """
        SELECT file, filename
        FROM assignment_files
        WHERE courseid = %s AND matid = %s AND fileid = %s
        """,
        (course_id, assignment_id, file_id)
    )
    return db_cursor.fetchone()
