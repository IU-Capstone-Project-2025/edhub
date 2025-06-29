def sql_insert_material(db_cursor, course_id, title, description, user_email):
    db_cursor.execute(
        "INSERT INTO course_materials (courseid, name, description, timeadded, author) VALUES (%s, %s, %s, now(), %s) RETURNING matid",
        (course_id, title, description, user_email),
    )
    return db_cursor.fetchone()[0]


def sql_delete_material(db_cursor, course_id, material_id):
    db_cursor.execute(
        "DELETE FROM course_materials WHERE courseid = %s AND matid = %s",
        (course_id, material_id),
    )


def sql_select_material(db_cursor, course_id, material_id):
    db_cursor.execute(
        """
        SELECT courseid, matid, timeadded, name, description, author
        FROM course_materials
        WHERE courseid = %s AND matid = %s
        """,
        (course_id, material_id),
    )
    return db_cursor.fetchone()


def sql_insert_material_attachment(db_cursor, course_id, material_id, filename, contents):
    db_cursor.execute(
        """
        INSERT INTO material_files 
        (courseid, matid, filename, file, upload_time)
        VALUES (%s, %s, %s, %s, now())
        RETURNING fileid, upload_time
        """,
        (course_id, material_id, filename, contents),
    )
    return db_cursor.fetchone()
