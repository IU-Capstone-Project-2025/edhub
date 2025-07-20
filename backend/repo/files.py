def sql_download_attachment(storage_db_cursor, file_id):
    storage_db_cursor.execute("SELECT content FROM files WHERE id = %s", (file_id, ))
    return storage_db_cursor.fetchone()[0]
