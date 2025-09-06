import uuid
from datetime import datetime

import factory

from simcc.schemas import user_model


class CreateUserFactory(factory.Factory):
    class Meta:
        model = user_model.UserSchema

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.Faker('password')


class UserFactory(factory.Factory):
    class Meta:
        model = user_model.User

    user_id = factory.LazyFunction(uuid.uuid4)
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    role = 'DEFAULT'
    password = factory.Faker('password')
    created_at = factory.LazyFunction(lambda: datetime.now().date())
    updated_atdate = None
    icon_url = factory.Faker('image_url')
    cover_url = factory.Faker('image_url')
