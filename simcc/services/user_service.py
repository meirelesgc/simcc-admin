from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from simcc.core.connection import Connection
from simcc.models import user_models
from simcc.repositories import user_repository
from simcc.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)


async def post_user(
    conn: Connection,
    user: user_models.CreateUser,
    role: str = 'DEFAULT',
):
    user = user_models.User(**user.model_dump(), role=role)
    user.password = get_password_hash(user.password)
    await user_repository.post_user(conn, user)
    return user


async def get_user(conn: Connection, id: UUID = None, email: EmailStr = None):
    users = await user_repository.get_user(conn, id, email)
    return users


async def put_user(conn: Connection, user: user_models.User):
    user.updated_at = datetime.now()
    user.password = get_password_hash(user.password)
    await user_repository.put_user(conn, user)
    return user


async def delete_user(conn: Connection, id: UUID = None):
    await user_repository.delete_user(conn, id)


async def login_for_access_token(
    conn: Connection,
    form_data: OAuth2PasswordRequestForm,
):
    user = await get_user(conn, None, form_data.username)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )
    if not verify_password(form_data.password, user['password']):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )
    access_token = create_access_token(data={'sub': user['email']})
    return {
        'access_token': access_token,
        'token_type': 'bearer',
    }


async def get_or_create_user_by_orcid(
    conn: Connection, orcid_claims: dict
) -> user_models.User:
    orcid_id = orcid_claims.get('sub')
    if not orcid_id:
        raise Exception("Claim 'sub' (ORCID iD) não encontrado.")

    SCRIPT_SQL = """
        SELECT  id, orcid_id, username, email, password, role, created_at,
            updated_at, deleted_at
        FROM users WHERE orcid_id = %(orcid_id)s
        """
    user = await conn.select(SCRIPT_SQL, {'orcid_id': orcid_id}, True)

    if user:
        return user_models.User(**user)

    new_user_data = user_models.CreateUser(
        email=f'{orcid_id}@orcid.placeholder',
        username=orcid_claims.get('name', orcid_id),
        password='a-random-password-since-login-is-external',
        orcid_id=orcid_id,
    )

    created_user = await post_user(conn, new_user_data)
    return created_user
