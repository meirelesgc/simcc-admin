from http import HTTPStatus
from uuid import uuid4

import pytest

from simcc.models.features import star_models
from tests.factories.features import star_factory


@pytest.mark.asyncio
async def test_post_star(client, create_user, get_token):
    user = await create_user()
    token = get_token(user)

    star_payload = star_factory.CreateStarFactory()

    response = client.post(
        '/stars/',
        headers={'Authorization': f'Bearer {token}'},
        json=star_payload.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.CREATED

    response_data = response.json()
    assert star_models.Star(**response_data)
    assert response_data['user_id'] == str(user.id)
    assert response_data['entry_id'] == str(star_payload.entry_id)


@pytest.mark.asyncio
async def test_post_star_not_authenticated(client):
    star_payload = star_factory.CreateStarFactory()
    response = client.post(
        '/stars/',
        json=star_payload.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_stars(client, create_user, create_star, get_token):
    user = await create_user()
    token = get_token(user)

    await create_star(user)
    await create_star(user)

    other_user = await create_user()
    await create_star(other_user)

    response = client.get(
        '/stars/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK

    response_data = response.json()
    assert len(response_data) == 2
    for star in response_data:
        assert star['user_id'] == str(user.id)


@pytest.mark.asyncio
async def test_get_stars_empty(client, create_user, get_token):
    user = await create_user()
    token = get_token(user)

    response = client.get(
        '/stars/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_stars_not_authenticated(client):
    response = client.get('/stars/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_star(client, create_user, create_star, get_token):
    user = await create_user()
    token = get_token(user)

    star_to_delete = await create_star(user)

    response = client.delete(
        f'/stars/{star_to_delete.entry_id}/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    get_response = client.get(
        '/stars/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert get_response.status_code == HTTPStatus.OK
    assert len(get_response.json()) == 0


@pytest.mark.asyncio
async def test_delete_star_not_found(client, create_user, get_token):
    user = await create_user()
    token = get_token(user)
    inexistent_entry_id = uuid4()

    response = client.delete(
        f'/stars/{inexistent_entry_id}/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert (
        response.json()['detail']
        == 'Star not found for this user and entry_id'
    )


@pytest.mark.asyncio
async def test_delete_star_from_another_user(
    client, create_user, create_star, get_token
):
    owner_user = await create_user()
    star_to_delete = await create_star(owner_user)

    attacker_user = await create_user()
    attacker_token = get_token(attacker_user)

    response = client.delete(
        f'/stars/{star_to_delete.entry_id}/',
        headers={'Authorization': f'Bearer {attacker_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_star_not_authenticated(client):
    entry_id = uuid4()
    response = client.delete(f'/stars/{entry_id}/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED
