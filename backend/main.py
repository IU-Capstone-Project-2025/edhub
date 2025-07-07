from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logic.users import create_admin_account as logic_create_admin_account
from auth import get_db

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

# TODO: прописать конкретные доверенные источники (на прод уже)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create an initial admin account
async def create_admin_account():
    with get_db() as (db_conn, db_cursor):
        password = logic_create_admin_account(db_conn, db_cursor)
        print(f"\nAdmin account created\nlogin: admin\npassword: {password}\n")

# app startup
@app.on_event("startup")
async def startup_event():
    await create_admin_account()
