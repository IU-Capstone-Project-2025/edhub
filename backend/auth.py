from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from contextlib import contextmanager
from secrets import token_hex
from jose import jwt, JWTError
from datetime import datetime

from psycopg2.pool import PoolError
from psycopg2.pool import ThreadedConnectionPool


def mk_database(dbname, user, password, host, port):
    conn_pool = ThreadedConnectionPool(
        minconn=2, maxconn=20, dbname=dbname, user=user, password=password, host=host, port=port
    )

    @contextmanager
    def get_conn():
        conn = None
        try:
            conn = conn_pool.getconn()
            cursor = conn.cursor()
            yield conn, cursor
        except PoolError:
            raise HTTPException(status_code=503, detail="All database connections are busy")
        finally:
            if conn:
                conn.commit()
                conn_pool.putconn(conn)

    return get_conn


get_db = mk_database(dbname="edhub", user="postgres", password="12345678", host="system_db", port="5432")


get_storage_db = mk_database(
    dbname="edhub_storage", user="postgres", password="12345678", host="filestorage_db", port="5432"
)


router = APIRouter()

# setting for JWT and autorization
SECRET_KEY = token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expire_timestamp = payload.get("exp")
        user_email = payload.get("email")

        # checking the fields
        if expire_timestamp is None or user_email is None:
            raise ValueError("Invalid token structure")
        
        # checking token expiration time
        if datetime.utcnow() > datetime.fromtimestamp(expire_timestamp):
            raise ValueError("Token expired")

    except (JWTError, ValueError) as e:
        detail = str(e) if str(e) else "Invalid token"
        raise HTTPException(status_code=401, detail=detail)

    # checking whether such user exists
    with get_db() as (db_conn, db_cursor):
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (user_email,))
        user_exists = db_cursor.fetchone()[0]
        if not user_exists:
            raise HTTPException(status_code=401, detail="User not exists")

    return user_email
