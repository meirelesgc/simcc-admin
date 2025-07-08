from datetime import datetime
from uuid import uuid4

import factory

from simcc.models.features import notification_models


class CreateNotificationFactory(factory.Factory):
    class Meta:
        model = notification_models.CreateNotification

    type = factory.Iterator([
        'NEW_PRODUCTION',
        'USER_FOLLOWED',
        'PRODUCTION_LIKED',
        'LATTES_REMINDER',
        'ORCID_REMINDER',
        'NEW_LOGIN',
    ])
    data = factory.Dict({'example': 'value'})
    user_id = factory.LazyFunction(uuid4)


class NotificationFactory(factory.Factory):
    class Meta:
        model = notification_models.Notification

    notification_id = factory.LazyFunction(uuid4)
    user_id = factory.LazyFunction(uuid4)
    sender_id = factory.LazyFunction(uuid4)
    type = factory.Iterator([
        'NEW_PRODUCTION',
        'USER_FOLLOWED',
        'PRODUCTION_LIKED',
        'LATTES_REMINDER',
        'ORCID_REMINDER',
        'NEW_LOGIN',
    ])
    data = factory.Dict({'example': 'value'})
    read = False
    created_at = factory.LazyFunction(datetime.now)
    read_at = None
