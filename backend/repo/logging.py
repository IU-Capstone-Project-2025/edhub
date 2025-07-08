import random

LOG_CLEANUP_PROBABILITY = 0.01


def sql_insert_log(db_cursor, tag, msg):
    db_cursor.execute("INSERT INTO logs (t, tag, msg) VALUES (now(), %s, %s)", (tag, msg))
    if random.random() < LOG_CLEANUP_PROBABILITY:
        sql_delete_old_logs(db_cursor)


def sql_delete_old_logs(db_cursor):
    db_cursor.execute("DELETE FROM logs WHERE t < NOW() - INTERVAl '7 days'")
