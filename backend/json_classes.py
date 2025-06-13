from pydantic import BaseModel


class Success(BaseModel):
    success: bool


class User(BaseModel):
    email: str
    name: str


class CourseId(BaseModel):
    course_id: str


class Course(BaseModel):
    course_id: str
    title: str
    creation_date: str
    number_of_students: int


class CourseFeed(BaseModel):
    course_id: str
    feed_id: int
    type: str


class MaterialID(BaseModel):
    course_id: str
    material_id: int


class Material(BaseModel):
    course_id: str
    material_id: int
    creation_date: str
    title: str
    description: str


class AssignmentID(BaseModel):
    course_id: str
    assignment_id: int


class Assignment(BaseModel):
    course_id: str
    assignment_id: int
    creation_date: str
    title: str
    description: str

class Submission(BaseModel):
    course_id: str
    assignment_id: int
    email: str
    name: str
    submission_time: str
    comment: str
    grade: str
    gradedby: str


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
