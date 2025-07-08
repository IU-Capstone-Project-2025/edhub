LOG_TRIGGER_COUNT = 100


def sql_insert_log(db_cursor, tag, msg):
    db_cursor.execute("INSERT INTO logs (t, tag, msg) VALUES (now(), %s, %s)", (tag, msg))
    # delete all logs on every LOG_TRIGGER_COUNT inserted
    db_cursor.execute("SELECT COUNT(*) FROM logs")
    log_count = db_cursor.fetchone()[0]
    if log_count % LOG_TRIGGER_COUNT == 0:
        sql_delete_old_logs(db_cursor)


def sql_delete_old_logs(db_cursor):
    db_cursor.execute("DELETE FROM logs WHERE t < NOW() - INTERVAl '7 days'")
