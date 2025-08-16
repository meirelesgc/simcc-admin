import uuid

import factory

from simcc.schemas import researcher_model


class CreateResearcherFactory(factory.Factory):
    class Meta:
        model = researcher_model.CreateResearcher

    name = factory.Faker('user_name')
    lattes_id = factory.Faker('bothify', text='################')
    institution_id = factory.LazyFunction(uuid.uuid4)
