from pydantic import BaseModel
from typing import Union
from sql.dto import UserEmailNameDTO, UserRolesDTO


class Success(BaseModel):
    success: bool


successful = Success(success=True)


class User(BaseModel):
    email: str
    name: str

    @staticmethod
    def from_dto(dto: UserEmailNameDTO) -> "User":
        return User(email=dto.email, name=dto.publicname)


class CourseRole(BaseModel):
    is_teacher: bool
    is_student: bool
    is_parent: bool
    is_admin: bool

    @staticmethod
    def from_dto(dto: UserRolesDTO) -> "CourseRole":
        return CourseRole(
            is_teacher=dto.is_teacher,
            is_student=dto.is_student,
            is_parent=dto.is_parent,
            is_admin=dto.is_admin,
        )


class CourseId(BaseModel):
    course_id: str


class Course(CourseId):
    title: str
    creation_time: str
    number_of_students: int


class CoursePost(BaseModel):
    course_id: str
    post_id: int
    type: str
    timeadded: str
    author: str


class MaterialID(BaseModel):
    course_id: str
    material_id: int


class Material(MaterialID):
    creation_time: str
    title: str
    description: str


class MaterialAttachmentMetadata(BaseModel):
    course_id: str
    material_id: int
    file_id: int
    filename: str
    upload_time: str


class AssignmentID(BaseModel):
    course_id: str
    assignment_id: int


class Assignment(AssignmentID):
    creation_time: str
    title: str
    description: str
    author: str


class AssignmentAttachmentMetadata(BaseModel):
    course_id: str
    assignment_id: int
    file_id: int
    filename: str
    upload_time: str


class Submission(BaseModel):
    course_id: str
    assignment_id: int
    student_email: str
    student_name: str
    submission_time: str
    last_modification_time: str
    comment: str
    grade: Union[int, None]
    gradedby_email: Union[str, None]


class SubmissionAttachmentMetadata(BaseModel):
    course_id: str
    assignment_id: int
    student_email: str
    file_id: int
    filename: str
    upload_time: str


class Account(BaseModel):
    email: str
    access_token: str


class UserCreate(BaseModel):
    email: str
    password: str
    name: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserNewPassword(BaseModel):
    email: str
    password: str
    new_password: str
