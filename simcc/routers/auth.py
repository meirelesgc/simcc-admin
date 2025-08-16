from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse

from simcc.config import Settings
from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.schemas import user_model
from simcc.security import (
    create_access_token,
    get_current_user,
    validate_google_token,
    validate_orcid_code,
)
from simcc.services import user_service

ORCID_CLIENT_ID = Settings().ORCID_CLIENT_ID
ORCID_REDIRECT_URI = Settings().ORCID_REDIRECT_URI
ORCID_OAUTH_URL = 'https://orcid.org/oauth/authorize'

GOOGLE_CLIENT_ID = Settings().GOOGLE_CLIENT_ID
GOOGLE_REDIRECT_URI = Settings().GOOGLE_REDIRECT_URI
GOOGLE_OAUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'

Conn = Annotated[Connection, Depends(get_conn)]
CurrentUser = Annotated[user_model.User, Depends(get_current_user)]

router = APIRouter()


@router.post('/token', response_model=user_model.Token)
async def login_for_access_token(
    conn: Conn, form_data: OAuth2PasswordRequestForm = Depends()
):
    return await user_service.login_for_access_token(conn, form_data)


@router.get('/auth/orcid/login')
async def orcid_login():
    params = {
        'client_id': ORCID_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid',
        'redirect_uri': ORCID_REDIRECT_URI,
    }
    auth_url = f'{ORCID_OAUTH_URL}?{"&".join([f"{k}={v}" for k, v in params.items()])}'  # noqa: E501
    return RedirectResponse(url=auth_url)


@router.get('/auth/orcid/callback', include_in_schema=False)
async def orcid_callback(code: str, conn: Conn):
    orcid_claims = await validate_orcid_code(code)
    user = await user_service.get_or_create_user_by_orcid(conn, orcid_claims)
    app_token = create_access_token(data={'sub': user.email})

    # Cria a resposta de redirecionamento
    response = RedirectResponse(url=Settings().FRONTEND_URL, status_code=302)

    # Armazena o token no cookie com as flags de segurança
    response.set_cookie(
        key='access_token',
        value=app_token,
        httponly=True,
        samesite='strict',
        # secure=True  # Usar em produção com HTTPS
    )
    return response


@router.get('/auth/shibboleth/login')
async def shibboleth_login(
    request: Request,
    conn: Conn,
):
    eppn = request.headers.get('eppn')
    name = request.headers.get('Shib-Person-CommonName')
    email = request.headers.get('shib-person-mail')

    if not eppn:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Atributo de identificação (eppn) não fornecido pelo Provedor de Identidade. Acesso negado.',  # noqa: E501
        )

    shib_user_data = {
        'eppn': eppn,
        'email': email or f'{eppn.split("@")[0]}@shibboleth.email',
        'name': name,
    }

    user = await user_service.get_or_create_user_by_shibboleth(
        conn, shib_user_data
    )
    app_token = create_access_token(data={'sub': user.email})

    # Cria a resposta de redirecionamento
    response = RedirectResponse(url=Settings().FRONTEND_URL, status_code=302)

    # Armazena o token no cookie com as flags de segurança
    response.set_cookie(
        key='access_token',
        value=app_token,
        httponly=True,
        samesite='strict',
        # secure=True # Usar em produção com HTTPS
    )
    return response


@router.get('/auth/google/login')
async def google_login():
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
    }
    auth_url = f'{GOOGLE_OAUTH_URL}?{"&".join([f"{k}={v}" for k, v in params.items()])}'
    return RedirectResponse(url=auth_url)


@router.get('/auth/google/callback', include_in_schema=False)
async def google_callback(code: str, conn: Conn):
    google_payload = await validate_google_token(code=code)
    user = await user_service.get_or_create_user_by_google(
        conn=conn, google_payload=google_payload
    )
    access_token = create_access_token(data={'sub': user.email})

    response = RedirectResponse(url=Settings().FRONTEND_URL, status_code=302)

    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        samesite='strict',
        # secure=True  # Usar em produção com HTTPS
    )
    return response


@router.post(
    '/key',
    response_model=user_model.KeyResponse,
    status_code=HTTPStatus.CREATED,
)
async def key_post(
    key: user_model.CreateKey,
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await user_service.key_post(conn, current_user, key)
