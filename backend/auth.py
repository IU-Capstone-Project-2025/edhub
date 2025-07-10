from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from secrets import token_hex
from jose import jwt, JWTError
from datetime import datetime
import edhub_errors
import database
import constraints


router = APIRouter()

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

        if expire_timestamp is None or user_email is None:
            raise edhub_errors.InvalidTokenStructureException()

        if datetime.utcnow() > datetime.fromtimestamp(expire_timestamp):
            raise edhub_errors.TokenExpiredException()

    except JWTError as e:
        detail = str(e)
        raise edhub_errors.CustomJWTException(detail)

    with database.get_system_conn() as db_conn, db_conn.cursor() as db_cursor:
        constraints.assert_user_exists(db_cursor, user_email)

    return user_email
