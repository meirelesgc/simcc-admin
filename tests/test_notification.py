from http import HTTPStatus

import pytest

from simcc.models.features import notification_models
from tests.factories.features import notification_factory


@pytest.mark.asyncio
async def test_post_notification(client, create_user, auth_header):
    user = await create_user()
    notification = notification_factory.CreateNotificationFactory(
        user_id=user.user_id
    )

    response = client.post(
        '/notification/',
        json=notification.model_dump(mode='json'),
        headers=auth_header(user),
    )

    assert response.status_code == HTTPStatus.CREATED
    assert notification_models.Notification(**response.json())


@pytest.mark.asyncio
async def test_get_notifications(
    client, create_user, create_notification, auth_header
):
    user = await create_user()
    AMONG = 1

    for _ in range(AMONG):
        await create_notification(user, user_id=user.user_id)

    response = client.get('/notification/', headers=auth_header(user))

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == AMONG


@pytest.mark.asyncio
async def test_get_notifications_by_other_user(
    client, create_user, create_notification, auth_header
):
    sender = await create_user()
    await create_notification(sender, user_id=sender.user_id)

    user = await create_user()
    response = client.get(
        '/notification/',
        headers=auth_header(user),
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_delete_notifications(
    client, create_user, create_notification, auth_header
):
    user = await create_user()
    AMONG = 1

    for _ in range(AMONG):
        notification = await create_notification(user, user_id=user.user_id)

    notification_id = notification.notification_id
    response = client.delete(
        f'/notification/{notification_id}/',
        headers=auth_header(user),
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
