from datetime import datetime


class AssignmentDTO:
    course_id: str
    assignment_id: int
    timeadded: datetime
    name: str
    description: str
    author_email: str

    def __init__(self, course_id: str, assignment_id: int, timeadded: datetime, name: str, description: str, author_email: str):
        self.course_id = course_id
        self.assignment_id = assignment_id
        self.timeadded = timeadded
        self.name = name
        self.description = description
        self.author_email = author_email


class AttachmentDTO:
    fileid: str
    filename: str
    uploadtime: datetime

    def __init__(self, fileid: str, filename: str, uploadtime: datetime):
        self.fileid = fileid
        self.filename = filename
        self.uploadtime = uploadtime


class CourseInfoDTO:
    course_id: str
    name: str
    time_created: datetime
    student_count: int

    def __init__(self, course_id: str, name: str, time_created: datetime, student_count: int):
        self.course_id = course_id
        self.name = name
        self.time_created = time_created
        self.student_count = student_count


class CourseFeedItemDTO:
    POST_ASSIGNMENT = 'ass'
    POST_MATERIAL = 'mat'
    course_id: str
    post_id: str
    post_type: str
    timeadded: datetime
    author_email: str

    def __init__(self, course_id: str, post_id: str, post_type: str, timeadded: datetime, author_email: str):
        self.course_id = course_id
        self.post_id = post_id
        self.post_type = post_type
        self.timeadded = timeadded
        self.author_email = author_email


class MaterialDTO:
    course_id: str
    material_id: str
    timeadded: datetime
    name: str
    description: str
    author_email: str

    def __init__(self, course_id: str, material_id: str, timeadded: datetime, name: str, description: str, author_email: str):
        self.course_id = course_id
        self.material_id = material_id
        self.timeadded = timeadded
        self.name = name
        self.description = description
        self.author_email = author_email
