from uuid import uuid4

import factory

from simcc.models.features import collection_models
from simcc.models.features.collection_models import CreateCollection


class CreateCollectionFactory(factory.Factory):
    class Meta:
        model = CreateCollection

    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('paragraph')


class CreateCollectionEntryFactory(factory.Factory):
    class Meta:
        model = collection_models.CreateCollectionEntry

    entry_id = factory.LazyFunction(uuid4)
    type = factory.Faker('word')
