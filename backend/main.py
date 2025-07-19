from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logic.users
from auth import get_db

import routers.assignments
import routers.submissions
import routers.courses
import routers.materials
import routers.parents
import routers.students
import routers.teachers
import routers.users


app = FastAPI(
    title="EdHub",
    description="**Open API for platform management**\n\n"
    "EdHub is a Learning Management System for interaction between "
    "teachers, students, and parents. It aims to improve the quality "
    "of an educational process, simplify the interaction between "
    "stakeholders, and improve student engagement in learning.\n\n"
    "Any user can create a course becoming a Teacher, invite students "
    "and their parents, upload materials, create assignments, see "
    " student submissions, grade them based on criteria, and calculate "
    "course grade. You can also join the course as a Student to see the "
    "study materials and submit your homework or as a Parent to track "
    "the academic performance of your child.\n\n"
    "Most existing LMSs either have limited functionality or have awkward "
    "website design and cause difficulties in everyday use. EdHub combines "
    "a self-contained and clear design, supporting all the necessary "
    "features but not bogging the user down with complex customizations.",
    version="1.0",
)
app.include_router(routers.assignments.router)
app.include_router(routers.submissions.router)
app.include_router(routers.courses.router)
app.include_router(routers.materials.router)
app.include_router(routers.parents.router)
app.include_router(routers.students.router)
app.include_router(routers.teachers.router)
app.include_router(routers.users.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app startup
@app.on_event("startup")
async def startup_event():
    with get_db() as (conn, cur):
        await logic.users.create_admin_account_if_not_exists(conn, cur)
