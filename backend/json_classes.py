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


class MaterialID(BaseModel):
    course_id: str
    material_id: int


class Material(BaseModel):
    course_id: str
    material_id: int
    creation_date: str
    title: str
    description: str


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
