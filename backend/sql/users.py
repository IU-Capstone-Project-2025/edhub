from sql.dto import UserEmailNameDTO


def get_user_name(conn, email: str) -> str:
    with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT publicname FROM users WHERE email = %s", (email,))
        return db_cursor.fetchone()[0]


def select_user_exists(conn, email: str) -> bool:
    with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (email,))
        return db_cursor.fetchone()[0]


def select_is_admin(conn, email: str) -> bool:
    with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT isadmin FROM users WHERE email = %s", (email,))
        return db_cursor.fetchone()[0]


def insert_user(conn, email: str, name: str, hashed_password: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "INSERT INTO users (email, publicname, isadmin, timeregistered, passwordhash) VALUES (%s, %s, 'f', now(), %s)",
            (email, name, hashed_password),
        )


def select_passwordhash(conn, email: str) -> str:
    with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT passwordhash FROM users WHERE email = %s", (email,))
        return db_cursor.fetchone()[0]


def update_password(conn, email: str, hashed_new_password: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute("UPDATE users SET passwordhash = %s WHERE email = %s", (hashed_new_password, email))


def select_single_teacher_courses(conn, user_email: str) -> list[str]:
    """
    Returns the list of course IDs where there is only one teacher
    """
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """SELECT t.courseid FROM teaches t WHERE t.email = %s AND
            (SELECT COUNT(*) FROM teaches WHERE courseid = t.courseid) = 1""",
            (user_email,),
        )
        return [row[0] for row in db_cursor.fetchall()]


def delete_user(conn, user_email: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute("DELETE FROM users WHERE email = %s", (user_email,))


def give_admin_permissions(conn, user_email: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute("UPDATE users SET isadmin = 't' WHERE email = %s", (user_email,))


def select_admins(conn) -> list[UserEmailNameDTO]:
    with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT email, publicname FROM users WHERE isadmin")
        return [UserEmailNameDTO(*attrs) for attrs in db_cursor.fetchall()]


def count_admins(conn) -> int:
    with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT COUNT(*) FROM users WHERE isadmin")
        return db_cursor.fetchone()[0]


def admins_exist(conn) -> bool:
    with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT EXISTS (SELECT 1 FROM users WHERE isadmin)")
        return db_cursor.fetchone()[0]


def select_all_users(conn) -> list[UserEmailNameDTO]:
    with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT email, publicname FROM users")
        return [UserEmailNameDTO(*attrs) for attrs in db_cursor.fetchall()]
