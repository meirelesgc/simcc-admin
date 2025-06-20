from datetime import datetime
from uuid import uuid4

import factory

from simcc.models import institution_model


class CreateInstitutionFactory(factory.Factory):
    class Meta:
        model = institution_model.CreateInstitution

    name = factory.Faker('company')
    acronym = factory.LazyAttribute(lambda o: o.name[:8].upper())


class InstitutionFactory(factory.Factory):
    class Meta:
        model = institution_model.Institution

    institution_id = factory.LazyFunction(uuid4)
    name = factory.Faker('company')
    acronym = factory.LazyAttribute(lambda o: o.name[:8].upper())
    created_at = factory.LazyFunction(datetime.now)
    updated_at = None
    deleted_at = None
