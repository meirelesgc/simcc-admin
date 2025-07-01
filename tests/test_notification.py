import pytest


@pytest.mark.asyncio
async def test_post_notfication(client, create_user, auth_header):
    user = await create_user()
    response = client.post(
        '/notification/',
        headers=auth_header(user),
    )
    # assert response.status_code == HTTPStatus.CREATED
