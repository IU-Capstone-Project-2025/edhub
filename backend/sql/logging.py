def insert_log(db_cursor, tag, msg):
    db_cursor.execute("INSERT INTO logs (t, tag, msg) VALUES (now(), %s, %s)", (tag, msg))
