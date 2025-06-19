import fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import http_errors

import routers.assignments
import routers.courses
import routers.materials
import routers.parents
import routers.students
import routers.teachers
import routers.users

app = FastAPI()


@app.exception_handler(http_errors.EdHubException)
async def edhub_exception_handler(request: fastapi.Request, exc: http_errors.EdHubException):
    return exc.json_response()


app.include_router(routers.assignments.router)
app.include_router(routers.courses.router)
app.include_router(routers.materials.router)
app.include_router(routers.parents.router)
app.include_router(routers.students.router)
app.include_router(routers.teachers.router)
app.include_router(routers.users.router)

# TODO: прописать конкретные доверенные источники (на прод уже)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
