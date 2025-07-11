def download_attachment(storage_conn, file_id: str) -> bytes:
    with storage_conn.cursor() as storage_db_cursor:
        storage_db_cursor.execute("SELECT content FROM files WHERE id = %s", (file_id,))
        return storage_db_cursor.fetchone()[0].tobytes()
