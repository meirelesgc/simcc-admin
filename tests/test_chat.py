import json
from http import HTTPStatus
from uuid import uuid4

import pytest
from starlette.testclient import WebSocketDenialResponse

from simcc.models.features import chat_model
from simcc.services.features import chat_service


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


@pytest.mark.asyncio
async def test_chat_message_get(client, create_user, auth_header):
    user = await create_user()
    AMONG = 1
    for _ in range(AMONG):
        client.post(
            f'/chat/user/{user.user_id}/',
            headers=auth_header(user),
            json={'content': 'Hello, world!'},
        )
    response = client.get(
        f'/chat/user/{user.user_id}/',
        headers=auth_header(user),
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == AMONG


@pytest.mark.asyncio
async def test_chat_between_two_users(
    client, create_user, get_token, redis, conn
):
    user = await create_user()
    URL = f'/ws/chat/user/{user.user_id}/?token={get_token(user)}'

    with client.websocket_connect(URL) as ws:
        confirmation = ws.receive_text()
        assert json.loads(confirmation) == {'status': 'connected'}

        users = [user.user_id, user.user_id]
        chat_id = await chat_service.fetch_chat_id(conn, users)
        key = f'chat:user:{chat_id}'

        await redis.publish(key, json.dumps({'message': 'Olá, tudo bem?'}))

        msg = ws.receive_text()
        data = json.loads(msg)
        assert data['message'] == 'Olá, tudo bem?'


@pytest.mark.asyncio
async def test_chat_message_post_unauthorized(client, create_user):
    user = await create_user()
    response = client.post(
        f'/chat/user/{user.user_id}/',
        json={'content': 'Hi without auth'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_chat_message_get_unauthorized(client, create_user):
    user = await create_user()
    response = client.get(f'/chat/user/{user.user_id}/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_chat_message_get_no_messages(client, create_user, auth_header):
    user = await create_user()
    response = client.get(
        f'/chat/user/{user.user_id}/',
        headers=auth_header(user),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_chat_message_ordering(client, create_user, auth_header):
    user = await create_user()
    messages = ['first', 'second', 'third']
    for msg in messages:
        client.post(
            f'/chat/user/{user.user_id}/',
            headers=auth_header(user),
            json={'content': msg},
        )
    response = client.get(
        f'/chat/user/{user.user_id}/', headers=auth_header(user)
    )
    payload = response.json()
    assert [m['content'] for m in payload] == messages


@pytest.mark.asyncio
async def test_websocket_invalid_token(client, create_user):
    user = await create_user()
    bad_token = 'invalid.token.here'
    URL = f'/ws/chat/user/{user.user_id}/?token={bad_token}'

    with pytest.raises(WebSocketDenialResponse) as response:
        with client.websocket_connect(URL):
            pass

    assert b'Could not validate credentials' in response.value.content


@pytest.mark.asyncio
async def test_websocket_send_and_receive_between_two_different_users(
    client, create_user, get_token
):
    alice = await create_user()
    bob = await create_user()

    alice_token = get_token(alice)
    bob_token = get_token(bob)

    URL_A = f'/ws/chat/user/{bob.user_id}/?token={alice_token}'
    URL_B = f'/ws/chat/user/{alice.user_id}/?token={bob_token}'

    with client.websocket_connect(URL_A) as ws_a:
        assert json.loads(ws_a.receive_text()) == {'status': 'connected'}
        with client.websocket_connect(URL_B) as ws_b:
            assert json.loads(ws_b.receive_text()) == {'status': 'connected'}

            ws_a.send_text('Oi Bob!')
            echo_data = json.loads(ws_b.receive_text())

            assert echo_data['sender_id'] == str(alice.user_id)
            assert echo_data['content'] == 'Oi Bob!'

            ws_b.send_text('Tudo bem Alice?')
            alice_receives_msg = ws_a.receive_text()
            msg_from_bob = json.loads(alice_receives_msg)
            assert msg_from_bob['sender_id'] == str(bob.user_id)
            assert msg_from_bob['content'] == 'Tudo bem Alice?'


@pytest.mark.asyncio
async def test_fetch_chat_id_consistency(conn):
    u1 = uuid4()
    u2 = uuid4()
    chat_id_1 = await chat_service.fetch_chat_id(conn, [u1, u2])
    chat_id_2 = await chat_service.fetch_chat_id(conn, [u2, u1])
    assert chat_id_1 == chat_id_2
    assert isinstance(chat_id_1, str)
