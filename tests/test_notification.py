import pytest


@pytest.mark.asyncio
async def test_post_notfication(client, create_user, auth_header):
    user = await create_user()
    notification = {'type': 'NEW_PRODUCTION', 'data': {}, 'user_id': '*'}
    client.post(
        '/notification/',
        json=notification,
        headers=auth_header(user),
    )
