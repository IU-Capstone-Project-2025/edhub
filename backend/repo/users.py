def sql_get_user_name(db_cursor, email):
    db_cursor.execute("SELECT publicname FROM users WHERE email = %s", (email,))
    return db_cursor.fetchone()[0]


def sql_select_user_exists(db_cursor, email):
    db_cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (email,))
    return db_cursor.fetchone()[0]


def sql_insert_user(db_cursor, email, name, hashed_password):
    db_cursor.execute(
        "INSERT INTO users (email, publicname, isadmin, timeregistered, passwordhash) VALUES (%s, %s, 'f', now(), %s)",
        (email, name, hashed_password),
    )


def sql_select_passwordhash(db_cursor, email):
    db_cursor.execute("SELECT passwordhash FROM users WHERE email = %s", (email,))
    return db_cursor.fetchone()


def sql_update_password(db_cursor, email, hashed_new_password):
    db_cursor.execute("UPDATE users SET passwordhash = %s WHERE email = %s", (hashed_new_password, email))


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


def sql_give_admin_permissions(db_cursor, user_email):
    db_cursor.execute("UPDATE users SET isadmin = 't' WHERE email = %s", (user_email,))


def sql_select_admins(db_cursor):
    db_cursor.execute("SELECT email, publicname FROM users WHERE isadmin")
    return db_cursor.fetchall()


def sql_count_admins(db_cursor):
    db_cursor.execute("SELECT COUNT(*) FROM users WHERE isadmin")
    return db_cursor.fetchone()[0]


def sql_admins_exist(db_cursor) -> bool:
    db_cursor.execute("SELECT EXISTS (SELECT 1 FROM users WHERE isadmin)")
    return db_cursor.fetchone()[0]


def sql_select_all_users(db_cursor):
    db_cursor.execute("SELECT email, publicname FROM users")
    return db_cursor.fetchall()
