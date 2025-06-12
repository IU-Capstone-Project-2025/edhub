from fastapi import FastAPI, HTTPException, Depends

# from auth import get_current_user, router as auth_router, get_db
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import router as auth_router
from routers.courses import router as courses_router
from routers.materials import router as materials_router
from routers.users import router as users_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(materials_router)
app.include_router(users_router)

# TODO: прописать конкретные доверенные источники (на прод уже)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
