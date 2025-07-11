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
