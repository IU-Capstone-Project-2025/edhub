def insert_assignment(db_cursor, course_id, title, description, user_email):
    db_cursor.execute(
        "INSERT INTO course_assignments (courseid, name, description, timeadded, author) VALUES (%s, %s, %s, now(), %s) RETURNING assid",
        (course_id, title, description, user_email),
    )
    return db_cursor.fetchone()[0]


def delete_assignment(db_cursor, course_id, assignment_id):
    db_cursor.execute(
        "DELETE FROM course_assignments WHERE courseid = %s AND assid = %s",
        (course_id, assignment_id),
    )


def select_assignment(db_cursor, course_id, assignment_id):
    db_cursor.execute(
        """
        SELECT courseid, assid, timeadded, name, description, author
        FROM course_assignments
        WHERE courseid = %s AND assid = %s
        """,
        (course_id, assignment_id),
    )
    return db_cursor.fetchone()


def insert_assignment_attachment(db_cursor, storage_db_cursor, course_id, assignment_id, filename, contents):
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
        INSERT INTO assignment_files 
        (courseid, assid, fileid, filename, uploadtime)
        VALUES (%s, %s, %s, %s, now())
        RETURNING fileid, uploadtime
        """,
        (course_id, assignment_id, fileid, filename),
    )
    return db_cursor.fetchone()


def select_assignment_attachments(db_cursor, course_id, assignment_id):
    db_cursor.execute(
        """
        SELECT fileid, filename, uploadtime
        FROM assignment_files
        WHERE courseid = %s AND assid = %s
        """,
        (course_id, assignment_id),
    )
    return db_cursor.fetchall()
