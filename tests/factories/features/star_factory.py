from uuid import uuid4

import factory

from simcc.models.features import star_models


class CreateStarFactory(factory.Factory):
    class Meta:
        model = star_models.CreateStar

    entry_id = factory.LazyFunction(uuid4)
    type = factory.Faker('word')


class StarFactory(factory.Factory):
    class Meta:
        model = star_models.Star

    user_id = factory.LazyFunction(uuid4)
    entry_id = factory.LazyFunction(uuid4)
    type = factory.Faker('word')
