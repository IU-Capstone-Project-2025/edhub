import constraints
import sql.materials as sql_mat
import sql.files as sql_files
from sql.dto import AttachmentInfoDTO


create_material = sql_mat.insert_material


remove_material = sql_mat.delete_material


get_material = sql_mat.select_material


create_material_attachment = sql_mat.insert_material_attachment


get_material_attachments = sql_mat.select_material_attachments


def download_material_attachment(
    conn, storage_conn, course_id: str, material_id: str, file_id: str, user_email: str
) -> tuple[AttachmentInfoDTO, bytes]:
    """
    Return the content of the file along with its metadata
    """
    constraints.assert_material_attachment_exists(conn, course_id, material_id)
    constraints.assert_file_exists(storage_conn, file_id)
    metadata = sql_mat.select_single_material_attachment(conn, course_id, material_id, file_id)
    content = sql_files.download_attachment(storage_conn, file_id)
    return metadata, content
