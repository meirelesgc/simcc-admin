from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_create_chat(conn, login_and_set_cookie, create_user):
    EXPECTED_COUNT = 1
    user1 = await create_user()
    user2 = await create_user()

    client = login_and_set_cookie(user1)

    users_id = [str(user1.user_id), str(user2.user_id)]
    payload = {'chat_name': 'XPTO', 'is_group': False, 'users': users_id}
    response = client.post('/chat/', json=payload)
    assert response.status_code == HTTPStatus.CREATED
    count = await conn.select('SELECT COUNT(*) FROM feature.chats', one=True)
    assert count.get('count') == EXPECTED_COUNT
