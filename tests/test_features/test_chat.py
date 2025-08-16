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


@pytest.mark.asyncio
async def test_websocket_link_valid_user(
    login_and_set_cookie, create_user, create_private_chat
):
    user1 = await create_user()
    user2 = await create_user()

    chat = await create_private_chat(user1, user2)

    client = login_and_set_cookie(user1)
    with client.websocket_connect(f'/ws/chat/{chat.chat_id}') as websocket:
        data = websocket.receive_json()
        assert data == {'status': 'connected'}


@pytest.mark.asyncio
async def test_websocket_message_flow(
    conn, login_and_set_cookie, create_user, create_private_chat
):
    user1 = await create_user()
    user2 = await create_user()

    chat = await create_private_chat(user1, user2)

    client = login_and_set_cookie(user1)

    with (
        client.websocket_connect(f'/ws/chat/{chat.chat_id}') as ws1,
        client.websocket_connect(f'/ws/chat/{chat.chat_id}') as ws2,
    ):
        assert ws1.receive_json() == {'status': 'connected'}
        assert ws2.receive_json() == {'status': 'connected'}

        message_text = 'Hello world'
        ws1.send_text(message_text)

        received = ws2.receive_json()

        assert 'message_id' in received
        assert received['chat_id'] == str(chat.chat_id)
        assert received['sender_id'] == str(user1.user_id)
        assert received['content'] == message_text
        assert 'created_at' in received

        row = await conn.select(
            'SELECT content FROM feature.chat_messages WHERE message_id = %(id)s',
            {'id': received['message_id']},
            one=True,
        )
        assert row['content'] == message_text


@pytest.mark.asyncio
async def test_get_chats(
    login_and_set_cookie, create_user, create_private_chat
):
    user1 = await create_user()
    user2 = await create_user()

    chat = await create_private_chat(user1, user2)

    client = login_and_set_cookie(user1)
    with client.websocket_connect(f'/ws/chat/{chat.chat_id}') as websocket:
        data = websocket.receive_json()
        assert data == {'status': 'connected'}
        message_text = 'Hellow!!'
        websocket.send_text(message_text)
    response = client.get('/chat/')
    print(response.json())
