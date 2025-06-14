from pydantic import BaseModel


class Success(BaseModel):
    success: bool


class User(BaseModel):
    email: str
    name: str


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


class AssignmentID(BaseModel):
    course_id: str
    assignment_id: int


class Assignment(AssignmentID):
    creation_time: str
    title: str
    description: str
    author: str

class Submission(BaseModel):
    course_id: str
    assignment_id: int
    student_email: str
    student_name: str
    submission_time: str
    last_modification_time: str
    comment: str
    grade: str
    gradedby_email: str


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
