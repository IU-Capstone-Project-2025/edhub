from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from contextlib import contextmanager
from pydantic import BaseModel
from secrets import token_hex
from jose import jwt
import psycopg2

@contextmanager
def get_db():
    conn = psycopg2.connect(dbname="edhub", user="postgres", password="12345678", host="db", port="5432")
    cursor = conn.cursor()
    try:
        yield conn, cursor
    finally:
        cursor.close()
        conn.close()

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
        user_email = payload.get("email")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    # checking whether such user exists
    with get_db() as (db_conn, db_cursor):
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (user_email,))
        user_exists = db_cursor.fetchone()[0]
        if not user_exists:
            raise HTTPException(status_code=401, detail="User not exists")
    
    return user_email

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

@router.post('/create_user')
async def create_user(user: UserCreate):

    with get_db() as (db_conn, db_cursor):

        # checking whether such user exists
        db_cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)", (user.email,))
        user_exists = db_cursor.fetchone()[0]
        if user_exists:
            raise HTTPException(status_code=400, detail="User already exists")
    
        # hashing password
        hashed_password = pwd_hasher.hash(user.password)
        db_cursor.execute(
            "INSERT INTO users (email, publicname, isadmin, timeregistered, passwordhash) VALUES (%s, %s, %s, now(), %s)",
            (user.email, user.name, False, hashed_password)
        )
        db_conn.commit()

    # giving access_token
    data = {"email": user.email, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return {"email": user.email, "success": True, "access_token": access_token}

class UserLogin(BaseModel):
    email: str
    password: str

@router.post('/login')
async def login(user: UserLogin):

    with get_db() as (db_conn, db_cursor):
        db_cursor.execute("SELECT passwordhash FROM users WHERE email = %s", (user.email,))
        result = db_cursor.fetchone()

        # checking whether such user exists
        if not result:
            raise HTTPException(status_code=401, detail="Invalid user email")

        # checking password
        hashed_password = result[0]
        if not pwd_hasher.verify(user.password, hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")
    
    # giving access token
    data = {"email": user.email, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return {"email": user.email, "success": True, "access_token": access_token}