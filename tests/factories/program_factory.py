import datetime

import factory
from faker import Faker

fake = Faker('pt_BR')


class GraduateProgramFactory(factory.DictFactory):
    graduate_program_id = factory.Faker('uuid4')
    code = factory.LazyFunction(
        lambda: fake.pystr(min_chars=5, max_chars=10).upper()
    )
    name = factory.LazyFunction(
        lambda: f'Programa de Pós-Graduação em {fake.bs().title()}'
    )
    name_en = factory.LazyFunction(
        lambda: f'Graduate Program in {fake.bs().title()}'
    )
    basic_area = factory.Faker(
        'random_element',
        elements=(
            'Ciências Exatas e da Terra',
            'Ciências Biológicas',
            'Engenharias',
            'Ciências da Saúde',
            'Ciências Agrárias',
            'Ciências Sociais Aplicadas',
            'Ciências Humanas',
            'Linguística, Letras e Artes',
        ),
    )
    cooperation_project = factory.Faker('company')
    area = factory.LazyAttribute(
        lambda obj: obj.basic_area
    )  # Assume a mesma área da básica para simplificar
    modality = factory.Faker(
        'random_element',
        elements=('Mestrado', 'Doutorado', 'Mestrado e Doutorado'),
    )
    program_type = factory.Faker(
        'random_element', elements=('Acadêmico', 'Profissional')
    )
    rating = factory.Faker(
        'random_element', elements=('3', '4', '5', '6', '7')
    )

    institution_id = factory.Faker('uuid4')

    state = 'BA'
    city = 'Salvador'
    region = 'Nordeste'
    url_image = factory.Faker('image_url')
    acronym = factory.LazyFunction(
        lambda: fake.pystr(min_chars=3, max_chars=5).upper()
    )
    description = factory.Faker('paragraph', nb_sentences=5)
    is_visible = factory.Faker('boolean')
    site = factory.Faker('url')
    coordinator = factory.Faker('name')
    email = factory.Faker('email')
    start = factory.Faker('date_object')
    phone = factory.LazyFunction(fake.phone_number)
    periodicity = factory.Faker(
        'random_element', elements=('Anual', 'Semestral')
    )

    created_at = factory.LazyFunction(datetime.datetime.now)
    updated_at = factory.LazyFunction(datetime.datetime.now)
    deleted_at = None
