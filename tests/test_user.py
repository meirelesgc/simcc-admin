from http import HTTPStatus

import pytest

from simcc.models import user_model
from tests.factories import user_factory


def test_post_user(client):
    user = user_factory.UserFactory()
    response = client.post('/user/', json=user.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.CREATED
    assert user_model.UserResponse(**response.json())


def test_get_users_unauthorized(client):
    response = client.get('/user/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_users_forbidden_to_default_user(
    client, create_user, get_token
):
    user = await create_user()
    headers = {'Authorization': f'Bearer {get_token(user)}'}

    response = client.get('/user/', headers=headers)
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_get_users_as_admin(
    client, create_user, create_admin_user, auth_header
):
    AMONG = 2
    await create_user()
    admin = await create_admin_user()

    response = client.get('/user/', headers=auth_header(admin))
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == AMONG


@pytest.mark.asyncio
async def test_get_single_user(client, create_user, auth_header):
    user = await create_user()
    response = client.get(f'/user/{user.user_id}/', headers=auth_header(user))
    assert response.status_code == HTTPStatus.OK
    data = user_model.UserResponse(**response.json())
    assert data.user_id == user.user_id


@pytest.mark.asyncio
async def test_get_single_user_by_admin(
    client, create_user, create_admin_user, auth_header
):
    user = await create_user()
    admin = await create_admin_user()

    response = client.get(f'/user/{user.user_id}/', headers=auth_header(admin))
    assert response.status_code == HTTPStatus.OK
    data = user_model.UserResponse(**response.json())
    assert data.user_id == user.user_id


@pytest.mark.asyncio
async def test_get_me(client, create_user, auth_header):
    user = await create_user()
    response = client.get('/user/my-self/', headers=auth_header(user))
    assert response.status_code == HTTPStatus.OK
    data = user_model.UserResponse(**response.json())
    assert data.user_id == user.user_id


@pytest.mark.asyncio
async def test_put_my_user(client, create_user, auth_header):
    user = await create_user()
    user.username = 'updated name'
    response = client.put(
        '/user/',
        headers=auth_header(user),
        json=user.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['username'] == 'updated name'
    assert response.json()['updated_at']


@pytest.mark.asyncio
async def test_put_user_by_other_user_forbidden(
    client, create_user, auth_header
):
    user = await create_user()
    other_user = await create_user()

    user.username = 'unauthorized update'
    response = client.put(
        '/user/',
        headers=auth_header(other_user),
        json=user.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_put_user_by_admin(
    client, create_user, create_admin_user, auth_header
):
    user = await create_user()
    admin = await create_admin_user()

    user.username = 'admin update'
    response = client.put(
        '/user/',
        headers=auth_header(admin),
        json=user.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['username'] == 'admin update'


@pytest.mark.asyncio
async def test_put_user_not_authenticated(client, create_user):
    user = await create_user()
    user.username = 'unauthenticated update'

    response = client.put(
        '/user/',
        headers={'Authorization': 'Bearer invalid_token'},
        json=user.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_user(client, create_user, auth_header):
    user = await create_user()
    token = auth_header(user)
    response = client.delete(
        f'/user/{user.user_id}/',
        headers=token,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get(f'/user/{user.user_id}/', headers=token)
    assert response.status_code == HTTPStatus.FORBIDDEN or HTTPStatus.NOT_FOUND
