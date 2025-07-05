from datetime import datetime


def sql_store_file(system_db_cursor, storage_db_cursor, filename: str, author: str, content: bytes) -> str:
    """
    Returns the uuid of a newly uploaded file.
    """
    storage_db_cursor.execute("INSERT INTO files VALUES (gen_random_uuid(), %s) RETURNING id", content)
    fileid = storage_db_cursor.fetchone()
    system_db_cursor.execute("INSERT INTO files VALUES (%s, %s, now(), %s)", fileid, filename, author)
    return fileid


def sql_select_file_metadata(system_db_cursor, id: str) -> tuple[str, datetime, str]:
    system_db_cursor.execute("SELECT name, uploadtime, author FROM files WHERE id = %s", id)
    return system_db_cursor.fetchone()


def sql_select_file_content(storage_db_cursor, id: str) -> bytes:
    storage_db_cursor.execute("SELECT content FROM files WHERE id = %s", id)
    return storage_db_cursor.fetchone()[0]
