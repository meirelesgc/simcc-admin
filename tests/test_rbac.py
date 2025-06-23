from http import HTTPStatus

import pytest


def test_post_role(client):
    role = {'name': 'test'}
    response = client.post('/role/', json=role)
    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_get_roles(client, create_role):
    AMONG = 2
    for _ in range(0, AMONG):
        await create_role()

    response = client.get('/role/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == AMONG


@pytest.mark.asyncio
async def test_put_role(client, create_role):
    ROLE_NAME = 'test_role'
    role = await create_role(name='XPTO')
    role.name = ROLE_NAME
    response = client.put(
        '/role/',
        json=role.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['name'] == ROLE_NAME


@pytest.mark.asyncio
async def test_delete_role(client, create_role):
    role = await create_role()
    response = client.delete(f'/role/{role.role_id}/')
    assert response.status_code == HTTPStatus.NO_CONTENT
    response = client.get('/role/')
    assert len(response.json()) == 0
