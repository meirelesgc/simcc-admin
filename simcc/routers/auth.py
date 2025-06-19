from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse

from simcc.config import Settings
from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.models import user_models
from simcc.security import create_access_token, validate_orcid_code
from simcc.services import user_service

ORCID_CLIENT_ID = Settings().ORCID_CLIENT_ID
ORCID_REDIRECT_URI = Settings().ORCID_REDIRECT_URI
ORCID_OAUTH_URL = 'https://orcid.org/oauth/authorize'

router = APIRouter()


@router.post('/token', response_model=user_models.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn: Connection = Depends(get_conn),
):
    return await user_service.login_for_access_token(conn, form_data)


@router.get('/orcid/login')
async def orcid_login():
    params = {
        'client_id': ORCID_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid',
        'redirect_uri': ORCID_REDIRECT_URI,
    }
    auth_url = f'{ORCID_OAUTH_URL}?{"&".join([f"{k}={v}" for k, v in params.items()])}'  # noqa: E501
    return RedirectResponse(url=auth_url)


@router.get('/orcid/callback')
async def orcid_callback(code: str, conn: Connection = Depends(get_conn)):
    orcid_claims = await validate_orcid_code(code)
    user = await user_service.get_or_create_user_by_orcid(conn, orcid_claims)
    app_token = create_access_token(data={'sub': user.email})
    return {'access_token': app_token, 'token_type': 'bearer'}
