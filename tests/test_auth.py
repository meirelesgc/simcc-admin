# from http import HTTPStatus

# import pytest


# @pytest.mark.asyncio
# async def test_get_token(client, create_user):
#     user = await create_user()
#     data = {'username': user.email, 'password': user.password}
#     response = client.post('/token', data=data)
#     token = response.json()
#     assert response.status_code == HTTPStatus.OK
#     assert 'access_token' in token
#     assert 'token_type' in token


# def test_orcid_redirect(client):
#     response = client.get('/auth/orcid/login', follow_redirects=False)
#     assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
#     assert 'location' in response.headers
#     assert response.headers['location'].startswith(
#         'https://orcid.org/oauth/authorize'
#     )


# @pytest.mark.asyncio
# async def test_orcid_callback_invalide_code(client):
#     fake_code = 'fake_auth_code'
#     response = client.get(f'/auth/orcid/callback?code={fake_code}')
#     assert response.status_code == HTTPStatus.BAD_REQUEST


# def test_post_key_unauthorized(client):
#     response = client.post('/key', json={'name': 'test'})
#     assert response.status_code == HTTPStatus.UNAUTHORIZED


# @pytest.mark.asyncio
# async def test_post_key(client, create_user, auth_header):
#     user = await create_user()
#     token = auth_header(user)
#     response = client.post(
#         '/key',
#         headers=token,
#         json={'name': 'test'},
#     )
#     assert response.status_code == HTTPStatus.CREATED
#     assert user_model.KeyResponse(**response.json())
