# checking whether the course exists in our LMS
from fastapi import HTTPException
import repository.courses as repo_courses


# TODO: why are the ids represented by strings instead of integers???
def assert_material_exists(db_cursor, course_id: str, material_id: str):
    try:
        material_id = int(material_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Material ID should be integer")

    repo_courses.assert_course_exists(db_cursor, course_id)
    db_cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM course_materials WHERE courseid = %s AND matid = %s  )",
        (course_id, material_id),
    )
    material_exists = db_cursor.fetchone()[0]
    if not material_exists:
        raise HTTPException(
            status_code=404, detail="No material with provided ID in this course"
        )
    return True
