from secrets import token_hex
from fastapi import HTTPException
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import repository.users as users_repo

SECRET_KEY = token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user_logic(db_conn, db_cursor, user):
    if users_repo.user_exists(db_cursor, user.email):
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = pwd_hasher.hash(user.password)
    users_repo.create_user(db_cursor, db_conn, user.email, user.name, hashed_password)
    data = {
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return {"email": user.email, "access_token": access_token}


def login_logic(db_cursor, user):
    hashed_password = users_repo.get_password_hash(db_cursor, user.email)
    if not hashed_password:
        raise HTTPException(status_code=401, detail="Invalid user email")
    if not pwd_hasher.verify(user.password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    data = {
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return {"email": user.email, "access_token": access_token}


def verify_token_logic(db_cursor, token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("email")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not users_repo.user_exists(db_cursor, user_email):
        raise HTTPException(status_code=401, detail="User not exists")
    return user_email
