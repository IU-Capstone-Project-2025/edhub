from datetime import datetime
from sql.dto import AssignmentDTO, AttachmentInfoDTO


def insert_assignment(conn, course_id: str, title: str, description: str, author_email: str) -> int:
    """
    Returns the ID of the new assignment within the course.
    """
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """INSERT INTO course_assignments (courseid, name, description, timeadded, author)
            VALUES (%s, %s, %s, now(), %s) RETURNING assid""",
            (course_id, title, description, author_email),
        )
        return db_cursor.fetchone()[0]


def delete_assignment(conn, course_id: str, assignment_id: int) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "DELETE FROM course_assignments WHERE courseid = %s AND assid = %s",
            (course_id, assignment_id),
        )


def select_assignment(conn, course_id: str, assignment_id: int) -> AssignmentDTO:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT courseid, assid, timeadded, name, description, author
            FROM course_assignments
            WHERE courseid = %s AND assid = %s
            """,
            (course_id, assignment_id),
        )
        return AssignmentDTO(*db_cursor.fetchone())


def insert_assignment_attachment(system_conn, storage_conn, course_id: str, assignment_id: int,
                                 filename: str, contents: bytes) -> tuple[str, datetime]:
    """
    Returns the fileid and uploadtime of the new file
    """
    with storage_conn.cursor() as storage_db_cursor:
        storage_db_cursor.execute(
            """
            INSERT INTO files
            (id, content)
            VALUES (gen_random_uuid(), %s)
            RETURNING id
            """,
            (contents, )
        )
        fileid = storage_db_cursor.fetchone()[0]

    with system_conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            INSERT INTO assignment_files
            (courseid, assid, fileid, filename, uploadtime)
            VALUES (%s, %s, %s, %s, now())
            RETURNING fileid, uploadtime
            """,
            (course_id, assignment_id, fileid, filename),
        )
        return db_cursor.fetchone()


def select_assignment_attachments(conn, course_id: str, assignment_id: int) -> list[AttachmentInfoDTO]:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT fileid, filename, uploadtime
            FROM assignment_files
            WHERE courseid = %s AND assid = %s
            """,
            (course_id, assignment_id),
        )
        return [AttachmentInfoDTO(*attrs) for attrs in db_cursor.fetchall()]


def sql_get_all_assignments(conn, course_id: str) -> list[int]:
    with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT assid FROM course_assignments WHERE courseid = %s",
                          (course_id,))
        return [i[0] for i in db_cursor.fetchall()]
