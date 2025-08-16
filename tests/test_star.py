from http import HTTPStatus
from uuid import uuid4

import pytest

from simcc.schemas.features import star_models
from tests.factories.features import star_factory


@pytest.mark.asyncio
async def test_post_star(client, create_user, login_and_set_cookie):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)

    star_payload = star_factory.CreateStarFactory()

    response = authenticated_client.post(
        '/stars/',
        json=star_payload.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.CREATED

    response_data = response.json()
    assert star_models.Star(**response_data)
    assert response_data['user_id'] == str(user.user_id)
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
async def test_get_stars(
    client, create_user, create_star, login_and_set_cookie
):
    AMONG = 2
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)

    await create_star(user)
    await create_star(user)

    # This star from another user should not appear in the results
    other_user = await create_user()
    await create_star(other_user)

    response = authenticated_client.get('/stars/')

    assert response.status_code == HTTPStatus.OK

    response_data = response.json()
    assert len(response_data) == AMONG
    for star in response_data:
        assert star['user_id'] == str(user.user_id)


@pytest.mark.asyncio
async def test_get_stars_empty(client, create_user, login_and_set_cookie):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)

    response = authenticated_client.get('/stars/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_stars_not_authenticated(client):
    response = client.get('/stars/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_star(
    client, create_user, create_star, login_and_set_cookie
):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)

    star_to_delete = await create_star(user)

    response = authenticated_client.delete(
        f'/stars/{star_to_delete.entry_id}/'
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    # Verify that the star was actually deleted
    get_response = authenticated_client.get('/stars/')
    assert get_response.status_code == HTTPStatus.OK
    assert len(get_response.json()) == 0


@pytest.mark.asyncio
async def test_delete_star_not_found(
    client, create_user, login_and_set_cookie
):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    inexistent_entry_id = uuid4()

    response = authenticated_client.delete(f'/stars/{inexistent_entry_id}/')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert (
        response.json()['detail']
        == 'Star not found for this user and entry_id'
    )


@pytest.mark.asyncio
async def test_delete_star_from_another_user(
    client, create_user, create_star, login_and_set_cookie
):
    # The user who owns the star
    owner_user = await create_user()
    star_to_delete = await create_star(owner_user)

    # The user trying to delete the star
    attacker_user = await create_user()
    authenticated_client = login_and_set_cookie(attacker_user)

    response = authenticated_client.delete(
        f'/stars/{star_to_delete.entry_id}/'
    )

    # The correct status should be NOT_FOUND because the star does not belong
    # to the authenticated user, so from their perspective, it doesn't exist.
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_star_not_authenticated(client):
    entry_id = uuid4()
    response = client.delete(f'/stars/{entry_id}/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED
