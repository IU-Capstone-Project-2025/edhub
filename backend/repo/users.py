def sql_select_user_exists(db_cursor, email):
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (email,))
    return db_cursor.fetchone()[0]


def sql_insert_user(db_cursor, email, name, hashed_password):
    db_cursor.execute(
        "INSERT INTO users (email, publicname, isadmin, timeregistered, passwordhash) VALUES (%s, %s, %s, now(), %s)",
        (email, name, False, hashed_password),
    )


def sql_select_passwordhash(db_cursor, email):
    db_cursor.execute("SELECT passwordhash FROM users WHERE email = %s", (email,))
    return db_cursor.fetchone()


def sql_select_single_teacher_courses(db_cursor, user_email):
    db_cursor.execute(
        "SELECT t.courseid FROM teaches t WHERE t.email = %s AND (SELECT COUNT(*) FROM teaches WHERE courseid = t.courseid) = 1",
        (user_email,),
    )
    return [row[0] for row in db_cursor.fetchall()]


def sql_delete_course(db_cursor, course_id):
    db_cursor.execute("DELETE FROM courses WHERE courseid = %s", (course_id,))


def sql_delete_user(db_cursor, user_email):
    db_cursor.execute("DELETE FROM users WHERE email = %s", (user_email,))
