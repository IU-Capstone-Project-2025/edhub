from fastapi import HTTPException
import repository.courses as courses_repo
import repository.users as users_repo
import repository.materials as mats_repo


def create_material_logic(
    db_cursor, db_conn, course_id, title, description, user_email
):
    courses_repo.assert_course_exists(db_cursor, course_id)
    users_repo.assert_teacher_access(db_cursor, user_email, course_id)
    material_id = mats_repo.create_material(
        db_cursor, db_conn, course_id, title, description
    )
    return {"course_id": course_id, "material_id": material_id}


def remove_material_logic(db_cursor, db_conn, course_id, material_id, user_email):
    mats_repo.assert_material_exists(db_cursor, course_id, material_id)
    users_repo.assert_teacher_access(db_cursor, user_email, course_id)
    mats_repo.remove_material(db_cursor, db_conn, course_id, material_id)
    return {"success": True}


def get_material_logic(db_cursor, course_id, material_id, user_email):
    courses_repo.assert_course_exists(db_cursor, course_id)
    courses_repo.assert_course_access(db_cursor, user_email, course_id)
    material = mats_repo.get_material(db_cursor, course_id, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return {
        "course_id": str(material[0]),
        "material_id": material[1],
        "creation_date": material[2].strftime("%m-%d-%Y %H:%M:%S"),
        "title": material[3],
        "description": material[4],
    }
