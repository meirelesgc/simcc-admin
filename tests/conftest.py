from http import HTTPStatus

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from simcc.app import app
from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.models.features import collection_models
from simcc.services import institution_service, user_service
from simcc.services.features import collection_service
from tests.factories import institution_factory, user_factory
from tests.factories.features import collection_factory


@pytest.fixture(scope='session', autouse=True)
def postgres():
    with PostgresContainer('pgvector/pgvector:pg17') as pg:
        yield pg


async def reset_database(conn: Connection):
    SCRIPT_SQL = """
        DROP SCHEMA IF EXISTS public CASCADE;
        DROP SCHEMA IF EXISTS ufmg CASCADE;
        DROP SCHEMA IF EXISTS feature CASCADE;
        CREATE SCHEMA public;
        """
    await conn.exec(SCRIPT_SQL)
    with open('init.sql', 'r', encoding='utf-8') as buffer:
        await conn.exec(buffer.read())


@pytest_asyncio.fixture
async def conn(postgres):
    connection_url = f'postgresql://{postgres.username}:{postgres.password}@{postgres.get_container_host_ip()}:{postgres.get_exposed_port(5432)}/{postgres.dbname}'
    conn = Connection(connection_url, max_size=20, timeout=10)
    await conn.connect()
    await reset_database(conn)
    yield conn
    await conn.disconnect()


@pytest.fixture
def client(conn):
    async def get_conn_override():
        yield conn

    app.dependency_overrides[get_conn] = get_conn_override

    return TestClient(app)


@pytest.fixture
def create_institution(conn):
    async def _create_institution(**kwargs):
        institution = institution_factory.CreateInstitutionFactory(**kwargs)
        institution = await institution_service.post_institution(
            institution, conn
        )
        return institution

    return _create_institution


@pytest.fixture
def create_user(conn):
    async def _create_user(**kwargs):
        raw_user = user_factory.CreateUserFactory(**kwargs)
        password = raw_user.password
        created_user = await user_service.post_user(
            conn, raw_user, role='DEFAULT'
        )
        created_user.password = password
        return created_user

    return _create_user


@pytest.fixture
def create_admin_user(conn):
    async def _create_admin_user(**kwargs):
        raw_user = user_factory.CreateUserFactory(**kwargs)
        password = raw_user.password
        created_user = await user_service.post_user(
            conn, raw_user, role='ADMIN'
        )
        created_user.password = password
        return created_user

    return _create_admin_user


@pytest.fixture
def get_token(client):
    def _get_token(user):
        data = {'username': user.email, 'password': user.password}
        response = client.post('/token', data=data)
        return response.json()['access_token']

    return _get_token


@pytest.fixture
def create_collection(conn):
    async def _create(user, **kwargs):
        collection = collection_factory.CreateCollectionFactory(**kwargs)
        return await collection_service.post_collection(
            conn, collection, current_user=user
        )

    return _create


@pytest.fixture
def create_entry_in_collection(client, get_token):
    async def _create_entry(collection, user):
        token = get_token(user)
        entry_data = collection_factory.CreateCollectionEntryFactory()
        entry_data = entry_data.model_dump(mode='json')
        response = client.post(
            f'/collection/{collection.collection_id}/entries/',
            headers={'Authorization': f'Bearer {token}'},
            json=entry_data,
        )
        assert response.status_code == HTTPStatus.CREATED
        return collection_models.CollectionEntry(**response.json())

    return _create_entry
