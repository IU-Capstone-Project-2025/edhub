from datetime import datetime
from sql.dto import MaterialDTO, AttachmentInfoDTO


def insert_material(conn, course_id: str, title: str, description: str, author_email: str) -> int:
    """
    Returns the ID of the new material within the course
    """
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """INSERT INTO course_materials (courseid, name, description, timeadded, author)
            VALUES (%s, %s, %s, now(), %s) RETURNING matid""",
            (course_id, title, description, author_email),
        )
        return db_cursor.fetchone()[0]


def delete_material(conn, course_id: str, material_id: int) -> None:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "DELETE FROM course_materials WHERE courseid = %s AND matid = %s",
            (course_id, material_id),
        )


def select_material(conn, course_id: str, material_id: int) -> MaterialDTO:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT timeadded, name, description, author
            FROM course_materials
            WHERE courseid = %s AND matid = %s
            """,
            (course_id, material_id),
        )
        return MaterialDTO(course_id, material_id, *db_cursor.fetchone())


def insert_material_attachment(system_conn, storage_conn, course_id: str,
                               material_id: int, filename: str, contents: bytes) -> tuple[str, datetime]:
    """
    Returns the ID and upload time of the created file
    """
    with storage_conn.cursor() as storage_db_cursor:
        storage_db_cursor.execute(
            """
            INSERT INTO files
            (id, content)
            VALUES (gen_random_uuid(), %s)
            RETURNING id
            """,
            (contents,)
        )
        fileid = storage_db_cursor.fetchone()[0]

    with system_conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            INSERT INTO material_files
            (courseid, matid, fileid, filename, uploadtime)
            VALUES (%s, %s, %s, %s, now())
            RETURNING fileid, uploadtime
            """,
            (course_id, material_id, fileid, filename),
        )
        return db_cursor.fetchone()


def select_material_attachments(conn, course_id: str, material_id: int) -> list[AttachmentInfoDTO]:
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            """
            SELECT fileid, filename, uploadtime
            FROM material_files
            WHERE courseid = %s AND matid = %s
            """,
            (course_id, material_id),
        )
        return [AttachmentInfoDTO(*attrs) for attrs in db_cursor.fetchall()]
