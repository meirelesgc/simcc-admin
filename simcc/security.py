from datetime import datetime, timedelta
from http import HTTPStatus
from typing import List
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.models import user_models

SECRET_KEY = 'your-secret-key'  # Buscar do .env
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    conn: Connection = Depends(get_conn),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject_email = payload.get('sub')
        if not subject_email:
            raise credentials_exception
    except (DecodeError, ExpiredSignatureError):
        raise credentials_exception

    SCRIPT_SQL = """
        SELECT id, username, email, role, password, created_at, updated_at,
            deleted_at
        FROM public.users
        WHERE email = %(email)s;
        """

    user = await conn.select(SCRIPT_SQL, {'email': subject_email}, True)

    if not user:
        raise credentials_exception

    return user_models.User(**user)


def authorize_user(allowed_roles: List[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get('role')
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='Not enough permissions',
            )
        return current_user

    return role_checker


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
