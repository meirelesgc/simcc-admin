from http import HTTPStatus

import pytest

from simcc.models.features import chat_model


@pytest.mark.asyncio
async def test_chat_message_post(client, create_user, auth_header):
    user = await create_user()
    response = client.post(
        f'/chat/user/{user.user_id}/',
        headers=auth_header(user),
        json={'content': 'Hello, world!'},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert chat_model.Message(**response.json())
