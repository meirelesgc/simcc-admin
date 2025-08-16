from datetime import datetime, timedelta
from http import HTTPStatus
from typing import List
from zoneinfo import ZoneInfo

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from jose import JWTError
from jose import jwt as jwtJose
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash

from simcc.config import Settings
from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.schemas import user_model

SECRET_KEY = 'your-secret-key'  # Buscar do .env
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 10080
pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

ORCID_TOKEN_URL = 'https://orcid.org/oauth/token'
ORCID_JWKS_URL = 'https://orcid.org/oauth/jwks'

GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'


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
        SELECT u.user_id, u.username, u.email, u.password, u.created_at,
            u.updated_at, ARRAY_REMOVE(ARRAY_AGG(p.name), NULL)
            AS permissions
        FROM public.users u
            LEFT JOIN user_roles ur
                ON ur.user_id = u.user_id
            LEFT JOIN role_permissions rp
                ON rp.role_id = ur.role_id
            LEFT JOIN permissions p
                ON p.permission_id = rp.permission_id
        WHERE email = %(email)s
        GROUP BY u.user_id;
        """

    user = await conn.select(SCRIPT_SQL, {'email': subject_email}, True)

    if not user:
        raise credentials_exception

    return user_model.UserPublic(**user)


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


async def validate_orcid_code(code: str) -> dict:
    token_request_payload = {
        'client_id': Settings().ORCID_CLIENT_ID,
        'client_secret': Settings().ORCID_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': Settings().ORCID_REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            ORCID_TOKEN_URL,
            data=token_request_payload,
        )
        if token_response.status_code != HTTPStatus.OK:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Falha ao trocar o código de autorização com o ORCID.',
            )

        token_data = token_response.json()
        id_token = token_data.get('id_token')
        access_token = token_data.get('access_token')

        if not id_token or not access_token:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Token de ID ou de Acesso não encontrado na resposta do ORCID.',  # noqa: E501
            )

        jwks_response = await client.get(ORCID_JWKS_URL)
        if jwks_response.status_code != HTTPStatus.OK:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Não foi possível obter as chaves de validação do ORCID.',  # noqa: E501
            )
        jwks = jwks_response.json()

    try:
        payload = jwtJose.decode(
            id_token,
            jwks,
            algorithms=['RS256'],
            audience=Settings().ORCID_CLIENT_ID,
            issuer='https://orcid.org',
            access_token=access_token,
        )
        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=f'Erro na validação do token ORCID: {e}',
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Erro inesperado no processamento do token: {e}',
        )


async def validate_google_token(code: str) -> dict:
    token_request_payload = {
        'code': code,
        'client_id': Settings().GOOGLE_CLIENT_ID,
        'client_secret': Settings().GOOGLE_CLIENT_SECRET,
        'redirect_uri': Settings().GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }

    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data=token_request_payload,
            )
            if token_response.status_code != HTTPStatus.OK:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail='Falha ao trocar o código de autorização com o GOOGLE.',  # noqa: E501
                )
            token_data = token_response.json()

        id_token_str = token_data.get('id_token')
        if not id_token_str:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Token de ID ou de Acesso não encontrado na resposta do GOOGLE.',  # noqa: E501
            )

        request = google_requests.Request()
        id_info = id_token.verify_oauth2_token(
            id_token_str, request, Settings().GOOGLE_CLIENT_ID
        )
        return id_info

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=f'Erro na validação do token GOOGLE: {e}',
        )
    except ValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Erro inesperado no processamento do token: {e}',
        )
