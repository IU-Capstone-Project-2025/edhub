import random
LOG_CLEANUP_PROBABILITY = 0.01


def insert_log(conn, tag: str, msg: str) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute("INSERT INTO logs (t, tag, msg) VALUES (now(), %s, %s)", (tag, msg))
    if random.random() < LOG_CLEANUP_PROBABILITY:
        delete_old_logs(conn)


def delete_old_logs(conn) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute("DELETE FROM logs WHERE t < NOW() - INTERVAl '7 days'")
