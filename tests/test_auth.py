from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_get_token(client, create_user):
    user = await create_user()
    data = {'username': user.email, 'password': user.password}
    response = client.post('/auth/token/', data=data)
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_orcid_redirect(client):
    response = client.get('/auth/orcid/login', follow_redirects=False)
    assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
    assert 'location' in response.headers
    assert response.headers['location'].startswith(
        'https://orcid.org/oauth/authorize'
    )


@pytest.mark.asyncio
async def test_orcid_callback_invalide_code(client):
    fake_code = 'fake_auth_code'
    response = client.get(f'/auth/orcid/callback?code={fake_code}')
    assert response.status_code == HTTPStatus.BAD_REQUEST


# @pytest.mark.asyncio
# async def test_orcid_callback_success(client):
#     fake_code = 'fake_auth_code'
#     response = client.get(f'/auth/orcid/callback?code={fake_code}')
#     assert response.status_code == HTTPStatus.BAD_REQUEST
