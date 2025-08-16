from http import HTTPStatus

import pytest

from simcc.schemas.features import notification_models
from tests.factories.features import notification_factory


@pytest.mark.asyncio
async def test_post_notification(client, create_user, login_and_set_cookie):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)

    notification = notification_factory.CreateNotificationFactory(
        user_id=user.user_id
    )

    response = authenticated_client.post(
        '/notification/',
        json=notification.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.CREATED
    assert notification_models.Notification(**response.json())


@pytest.mark.asyncio
async def test_post_notification_for_any_users(
    client, create_user, login_and_set_cookie
):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)

    notification = notification_factory.CreateNotificationFactory(user_id='*')

    response = authenticated_client.post(
        '/notification/',
        json=notification.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.CREATED
    assert notification_models.Notification(**response.json())


@pytest.mark.asyncio
async def test_get_notifications(
    client, create_user, create_notification, login_and_set_cookie
):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    AMONG = 1

    for _ in range(AMONG):
        await create_notification(user, user_id=user.user_id)

    response = authenticated_client.get('/notification/')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == AMONG


@pytest.mark.asyncio
async def test_get_notifications_by_other_user(
    client, create_user, create_notification, login_and_set_cookie
):
    # Cria uma notificação para o usuário 'sender'
    sender = await create_user()
    await create_notification(sender, user_id=sender.user_id)

    # Autentica como um usuário diferente, que não deve ver a notificação acima
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)

    response = authenticated_client.get('/notification/')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_get_notifications_by_other_user_with_any(
    client,
    create_user,
    create_admin_user,
    create_notification,
    login_and_set_cookie,
):
    sender = await create_admin_user()
    user = await create_user()

    response = await create_notification(sender, user_id='*')

    authenticated_client = login_and_set_cookie(user)

    response = authenticated_client.get('/notification/')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_delete_notifications(
    client, create_user, create_notification, login_and_set_cookie
):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    AMONG = 1

    for _ in range(AMONG):
        notification = await create_notification(user, user_id=user.user_id)

    notification_id = notification.notification_id
    response = authenticated_client.delete(f'/notification/{notification_id}/')

    assert response.status_code == HTTPStatus.NO_CONTENT
