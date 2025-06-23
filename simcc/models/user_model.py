import uuid
from datetime import datetime

import factory

from simcc.models import user_model


class CreateUserFactory(factory.Factory):
    class Meta:
        model = user_model.CreateUser

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.Faker('password')


class UserFactory(factory.Factory):
    class Meta:
        model = user_model.User

    user_id = factory.LazyFunction(uuid.uuid4)
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.Faker('password')
    created_at = factory.LazyFunction(datetime.now)
    updated_at = None
