import fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logic.users
import edhub_errors
import database

import routers.assignments
import routers.submissions
import routers.courses
import routers.materials
import routers.parents
import routers.students
import routers.teachers
import routers.users


app = FastAPI()
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


@app.exception_handler(edhub_errors.EdHubException)
async def edhub_exception_handler(request: fastapi.Request, exc: edhub_errors.EdHubException):
    return exc.json_response()


@app.on_event("startup")
async def startup_event():
    with database.get_system_conn() as conn:
        logic.users.create_admin_account_if_not_exists(conn)
