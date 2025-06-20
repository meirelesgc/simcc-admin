import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from simcc.app import app
from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.services import institution_service, user_service
from tests.factories import institution_factory, user_factory


@pytest.fixture(scope='session', autouse=True)
def postgres():
    with PostgresContainer('pgvector/pgvector:pg17') as pg:
        yield pg


async def reset_database(conn: Connection):
    SCRIPT_SQL = """
        DROP SCHEMA IF EXISTS public CASCADE;
        DROP SCHEMA IF EXISTS ufmg CASCADE;
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
        response = client.post('/auth/token/', data=data)
        return response.json()['access_token']

    return _get_token
