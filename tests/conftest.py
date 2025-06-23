from http import HTTPStatus

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from simcc.app import app
from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.models import rbac_model
from simcc.models.features import collection_models
from simcc.services import institution_service, rbac_service, user_service
from simcc.services.features import collection_service, star_service
from tests.factories import institution_factory, rbac_factory, user_factory
from tests.factories.features import collection_factory, star_factory


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
        created_user = await user_service.post_user(conn, raw_user)
        created_user.password = password
        return created_user

    return _create_user


@pytest.fixture
def create_admin_user(conn, create_role):
    async def _create_admin_user(**kwargs):
        user = await _create_user_with_password(conn, **kwargs)
        role = await _assign_role_to_user(conn, create_role, user.user_id)
        await _assign_admin_permission_to_role(conn, role.role_id)
        return user

    return _create_admin_user


async def _create_user_with_password(conn, **kwargs):
    raw_user = user_factory.CreateUserFactory(**kwargs)
    password = raw_user.password
    user = await user_service.post_user(conn, raw_user)
    user.password = password
    return user


async def _assign_role_to_user(conn, create_role, user_id):
    role = await create_role()
    user_role = rbac_model.CreateUserRole(
        role_id=role.role_id, user_id=user_id
    )
    await rbac_service.post_user_role(conn, user_role)
    return role


async def _assign_admin_permission_to_role(conn, role_id):
    permissions = await rbac_service.get_permissions(conn)

    for p in permissions:
        if p['name'] == 'ADMIN':
            admin = p
    rp = {'permission_id': admin['permission_id'], 'role_id': role_id}
    rp = rbac_model.CreateRolePermission(**rp)
    await rbac_service.post_role_permissions(conn, rp)


@pytest.fixture
def create_role(conn):
    async def _create_role(**kwargs):
        payload = rbac_factory.CreateRoleFactory(**kwargs)
        created_role = await rbac_service.post_role(conn, payload)
        return created_role

    return _create_role


@pytest.fixture
def auth_header(get_token):
    def _auth_header(user):
        return {'Authorization': f'Bearer {get_token(user)}'}

    return _auth_header


@pytest.fixture
def get_token(client):
    def _get_token(user):
        data = {'username': user.email, 'password': user.password}
        response = client.post('/token/', data=data)
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


@pytest.fixture
def create_star(conn):
    async def _create_star(user):
        star_payload = star_factory.CreateStarFactory()
        created_star = await star_service.post_star(conn, star_payload, user)
        return created_star

    return _create_star
