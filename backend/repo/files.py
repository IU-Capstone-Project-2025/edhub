def sql_download_attachment(storage_db_cursor, file_id):
    storage_db_cursor.execute("SELECT content FROM files WHERE id = %s", (file_id, ))
    return storage_db_cursor.fetchone()[0]


def sql_select_attachment_metadata(db_cursor, file_id):
    db_cursor.execute("""
                      (SELECT fileid, filename, uploadtime FROM material_files WHERE fileid = %s)
                      UNION
                      (SELECT fileid, filename, uploadtime FROM assignment_files WHERE fileid = %s)
                      UNION
                      (SELECT fileid, filename, uploadtime FROM submissions_files WHERE fileid = %s)
                      """, (file_id, file_id, file_id))
    return db_cursor.fetchone()
