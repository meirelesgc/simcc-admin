from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_post_role_as_admin(
    client, create_admin_user, login_and_set_cookie
):
    admin = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin)

    role_payload = {'name': 'test_admin_role'}
    response = authenticated_client.post('/role/', json=role_payload)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['name'] == role_payload['name']


@pytest.mark.asyncio
async def test_get_roles_as_admin(
    client, create_role, create_admin_user, login_and_set_cookie
):
    admin = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin)

    # +1 because the admin user creation might create roles
    initial_count = len((authenticated_client.get('/role/')).json())

    AMONG = 2
    for _ in range(AMONG):
        await create_role()

    response = authenticated_client.get('/role/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == initial_count + AMONG


@pytest.mark.asyncio
async def test_put_role_as_admin(
    client, create_role, create_admin_user, login_and_set_cookie
):
    admin = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin)

    UPDATED_ROLE_NAME = 'updated_role_name'
    role = await create_role(name='original_name')
    role.name = UPDATED_ROLE_NAME

    response = authenticated_client.put(
        '/role/',
        json=role.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['name'] == UPDATED_ROLE_NAME


@pytest.mark.asyncio
async def test_delete_role_as_admin(
    client, create_role, create_admin_user, login_and_set_cookie
):
    admin = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin)

    role_to_delete = await create_role()
    initial_count = len((authenticated_client.get('/role/')).json())

    response = authenticated_client.delete(f'/role/{role_to_delete.role_id}/')
    assert response.status_code == HTTPStatus.NO_CONTENT

    # Verify the count decreased by one
    response = authenticated_client.get('/role/')
    assert len(response.json()) == initial_count - 1


@pytest.mark.asyncio
async def test_get_permissions_as_admin(
    client, create_admin_user, login_and_set_cookie
):
    admin = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin)

    response = authenticated_client.get('/permission/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_post_user_role_as_admin(
    client, create_role, create_user, create_admin_user, login_and_set_cookie
):
    admin = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin)

    role = await create_role()
    user = await create_user()

    user_role_payload = {
        'role_id': str(role.role_id),
        'user_id': str(user.user_id),
    }

    response = authenticated_client.post('/user/role/', json=user_role_payload)
    assert response.status_code == HTTPStatus.CREATED


# WIP -> Bloquear todas as rotas
@pytest.mark.asyncio
async def test_post_role_unauthorized(client):
    role_payload = {'name': 'test_unauth_role'}
    response = client.post('/role/', json=role_payload)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_post_role_forbidden(client, create_user, login_and_set_cookie):
    regular_user = await create_user()
    authenticated_client = login_and_set_cookie(regular_user)

    role_payload = {'name': 'test_forbidden_role'}
    response = authenticated_client.post('/role/', json=role_payload)
    assert response.status_code == HTTPStatus.FORBIDDEN
