from http import HTTPStatus

import pytest

from simcc.models import user_models
from tests.factories import user_factory


def test_post_user(client):
    user = user_factory.UserFactory()
    response = client.post('/user/', json=user.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.CREATED
    assert user_models.UserResponse(**response.json())


def test_get_users(client):
    LENGTH = 0
    response = client.get('/user/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_get_one_users(client, create_user):
    LENGTH = 1

    for _ in range(0, LENGTH):
        await create_user()

    response = client.get('/user/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_get_two_users(client, create_user):
    LENGTH = 2

    for _ in range(0, LENGTH):
        await create_user()

    response = client.get('/user/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_get_single_user(client, create_user):
    user = await create_user()
    response = client.get(f'/user/{user.id}/')
    assert response.status_code == HTTPStatus.OK
    assert user_models.UserResponse(**response.json())


@pytest.mark.asyncio
async def test_put_my_user(client, create_user, get_token):
    user = await create_user()
    user.username = 'updated name'
    response = client.put(
        '/user/',
        headers={'Authorization': f'Bearer {get_token(user)}'},
        json=user.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.OK
    assert user_models.UserResponse(**response.json())
    assert response.json()['updated_at']


@pytest.mark.asyncio
async def test_put_user_by_other_user(client, create_user, get_token):
    other_user = await create_user()
    user = await create_user()
    user.username = 'updated name'
    response = client.put(
        '/user/',
        headers={'Authorization': f'Bearer {get_token(other_user)}'},
        json=user.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_put_user_by_admin_user(
    client, create_user, create_admin_user, get_token
):
    admin_user = await create_admin_user()
    user = await create_user()
    user.username = 'updated name'
    response = client.put(
        '/user/',
        headers={'Authorization': f'Bearer {get_token(admin_user)}'},
        json=user.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.OK
    assert user_models.UserResponse(**response.json())
    assert response.json()['updated_at']


@pytest.mark.asyncio
async def test_put_user_not_authenticated(client, create_user):
    user = await create_user()
    user.username = 'updated name'
    response = client.put(
        '/user/',
        headers={'Authorization': 'Bearer Not authenticated'},
        json=user.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_put_user_by_default_user_to_admin_role(
    client, create_user, get_token
):
    default_user = await create_user()
    token = get_token(default_user)

    update_payload = default_user.model_dump(mode='json')
    update_payload['role'] = 'ADMIN'

    response = client.put(
        '/user/',
        headers={'Authorization': f'Bearer {token}'},
        json=update_payload,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()['detail'] == 'Not enough permissions'


@pytest.mark.asyncio
async def test_delete_user(client, create_user, get_token):
    user = await create_user()
    response = client.delete(
        f'/user/{user.id}/',
        headers={'Authorization': f'Bearer {get_token(user)}'},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    LENGTH = 0
    response = client.get('/user/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_get_token(client, create_user):
    user = await create_user()
    data = {'username': user.email, 'password': user.password}
    response = client.post('/token/', data=data)
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token
