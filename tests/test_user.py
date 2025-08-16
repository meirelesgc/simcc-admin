from http import HTTPStatus

import pytest

from tests.factories import user_factory


@pytest.mark.asyncio
async def test_post_user(client, conn):
    EXPECTED_COUNT = 1
    user = user_factory.UserFactory()
    response = client.post('/user/', json=user.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.CREATED
    COUNT = await conn.select('SELECT COUNT(*) FROM users', one=True)
    assert COUNT.get('count') == EXPECTED_COUNT


def test_get_users_unauthorized(client):
    response = client.get('/user/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_users_forbidden_to_default_user(
    client, create_user, login_and_set_cookie
):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    response = authenticated_client.get('/user/')
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_get_users_as_admin(
    client, create_user, create_admin_user, login_and_set_cookie
):
    EXPECTED_COUNT = 2
    await create_user()
    admin = await create_admin_user()

    authenticated_client = login_and_set_cookie(admin)
    response = authenticated_client.get('/user/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == EXPECTED_COUNT


@pytest.mark.asyncio
async def test_get_single_user(client, create_user, login_and_set_cookie):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    response = authenticated_client.get(f'/user/{user.user_id}/')
    assert response.status_code == HTTPStatus.OK
    assert response.json().get('user_id') == str(user.user_id)


@pytest.mark.asyncio
async def test_get_single_user_by_admin(
    client, create_user, create_admin_user, login_and_set_cookie
):
    user = await create_user()
    admin = await create_admin_user()

    authenticated_client = login_and_set_cookie(admin)
    response = authenticated_client.get(f'/user/{user.user_id}/')
    assert response.status_code == HTTPStatus.OK
    assert response.json().get('user_id') == str(user.user_id)


@pytest.mark.asyncio
async def test_get_me(client, create_user, login_and_set_cookie):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    response = authenticated_client.get('/user/my-self/')
    assert response.status_code == HTTPStatus.OK
    assert response.json().get('user_id') == str(user.user_id)


@pytest.mark.asyncio
async def test_put_my_user(client, create_user, login_and_set_cookie):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    user.username = 'updated name'
    response = authenticated_client.put(
        '/user/',
        json=user.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json().get('username') == 'updated name'
    assert response.json().get('updated_at')


@pytest.mark.asyncio
async def test_put_user_by_other_user_forbidden(
    client, create_user, login_and_set_cookie
):
    user = await create_user()
    other_user = await create_user()

    authenticated_client = login_and_set_cookie(other_user)

    user.username = 'unauthorized update'
    response = authenticated_client.put(
        '/user/',
        json=user.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_put_user_by_admin(
    client, create_user, create_admin_user, login_and_set_cookie
):
    user = await create_user()
    admin = await create_admin_user()

    authenticated_client = login_and_set_cookie(admin)

    user.username = 'admin update'
    response = authenticated_client.put(
        '/user/',
        json=user.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json().get('username') == 'admin update'


@pytest.mark.asyncio
async def test_put_user_not_authenticated(client, create_user):
    user = await create_user()
    user.username = 'unauthenticated update'

    # Não define o cookie de autenticação no cliente.
    response = client.put(
        '/user/',
        json=user.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_single_user_forbidden(
    client, create_user, login_and_set_cookie
):
    user_one = await create_user()
    user_two = await create_user()

    authenticated_client = login_and_set_cookie(user_one)

    response = authenticated_client.get(f'/user/{user_two.user_id}/')

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_delete_user_forbidden(
    client, create_user, login_and_set_cookie
):
    user_one = await create_user()
    user_two = await create_user()

    authenticated_client = login_and_set_cookie(user_one)

    response = authenticated_client.delete(f'/user/{user_two.user_id}/')

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_delete_user(client, create_user, login_and_set_cookie):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    response = authenticated_client.delete(f'/user/{user.user_id}/')

    assert response.status_code == HTTPStatus.NO_CONTENT

    response = authenticated_client.get(f'/user/{user.user_id}/')
    assert response.status_code == HTTPStatus.FORBIDDEN or HTTPStatus.NOT_FOUND
