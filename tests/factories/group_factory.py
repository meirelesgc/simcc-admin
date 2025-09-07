from uuid import uuid4

import factory

from simcc.schemas.group_schemas import GroupSchema


class GroupFactory(factory.Factory):
    class Meta:
        model = GroupSchema

    name = factory.Faker('bs')
    group_identifier = factory.Faker('bothify', text='GRP-????-####')

    institution = factory.Faker('company')
    first_leader = factory.Faker('name')
    first_leader_id = factory.LazyFunction(uuid4)
    second_leader = factory.Faker('name')
    second_leader_id = factory.LazyFunction(uuid4)
    area = factory.Faker('job')
    census = factory.Faker('random_int', min=1000, max=99999)
    start_of_collection = factory.Faker('iso8601')
    end_of_collection = factory.Faker('iso8601')
    year = factory.Faker('year')
    institution_name = factory.Faker('company')
    category = factory.Faker('word')
