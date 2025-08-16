from datetime import datetime
from uuid import uuid4

import factory

from simcc.schemas import rbac_model


class CreateRoleFactory(factory.Factory):
    class Meta:
        model = rbac_model.CreateRole

    name = factory.Faker('word')


class RoleFactory(factory.Factory):
    class Meta:
        model = rbac_model.Role

    role_id = factory.LazyFunction(uuid4)
    name = factory.Faker('word')
    created_at = factory.LazyFunction(datetime.now)
    updated_at = None
    deleted_at = None
