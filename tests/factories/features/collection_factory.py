import factory

from simcc.models.features.collection_models import CreateCollection


class CreateCollectionFactory(factory.Factory):
    class Meta:
        model = CreateCollection

    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('paragraph')
