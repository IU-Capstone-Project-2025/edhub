from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from contextlib import contextmanager
import psycopg2
import models.api
import logic.auth as auth_logic


@contextmanager
def get_db():
    conn = psycopg2.connect(
        dbname="edhub", user="postgres", password="12345678", host="db", port="5432"
    )
    cursor = conn.cursor()
    try:
        yield conn, cursor
    finally:
        cursor.close()
        conn.close()


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    with get_db() as (db_conn, db_cursor):
        return auth_logic.verify_token_logic(db_cursor, token)


@router.post("/create_user", response_model=models.api.Account)
async def create_user(user: models.api.UserCreate):
    with get_db() as (db_conn, db_cursor):
        return auth_logic.create_user_logic(db_conn, db_cursor, user)


@router.post("/login", response_model=models.api.Account)
async def login(user: models.api.UserLogin):
    with get_db() as (db_conn, db_cursor):
        return auth_logic.login_logic(db_cursor, user)
