from http import HTTPStatus
from uuid import uuid4

import pytest

from simcc.models.features import collection_models
from tests.factories.features import collection_factory


@pytest.mark.asyncio
async def test_post_collection(client, create_user, get_token):
    user = await create_user()
    collection = collection_factory.CreateCollectionFactory()
    response = client.post(
        '/collection/',
        headers={'Authorization': f'Bearer {get_token(user)}'},
        json=collection.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.CREATED
    assert collection_models.CreateCollection(**response.json())


@pytest.mark.asyncio
async def test_get_collections(
    client, create_user, get_token, create_collection
):
    AMONG = 2
    user = await create_user()
    token = get_token(user)
    for _ in range(AMONG):
        await create_collection(user=user)

    response = client.get(
        '/collection/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == AMONG


@pytest.mark.asyncio
async def test_get_collection_by_id(
    client, create_user, get_token, create_collection
):
    user = await create_user()
    token = get_token(user)

    collection = await create_collection(user)

    response = client.get(
        f'/collection/{collection.collection_id}/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['collection_id'] == str(collection.collection_id)


@pytest.mark.asyncio
async def test_get_public_collections(client, create_user, create_collection):
    user = await create_user()
    await create_collection(user)

    response = client.get(f'/collection/public/{user.id}/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_delete_collection(
    client, create_user, get_token, create_collection
):
    user = await create_user()
    token = get_token(user)
    collection = await create_collection(user)

    response = client.delete(
        f'/collection/{collection.collection_id}/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get(
        '/collection/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_get_collection_by_id_not_found(client, create_user, get_token):
    user = await create_user()
    token = get_token(user)

    non_existent_id = uuid4()
    response = client.get(
        f'/collection/{non_existent_id}/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_update_collection(
    client, create_user, get_token, create_collection
):
    user = await create_user()
    token = get_token(user)
    collection = await create_collection(user=user)

    collection.name = 'Novo Nome da Coleção'
    collection.description = 'Nova descrição.'
    collection.visible = False

    response = client.put(
        '/collection/',
        headers={'Authorization': f'Bearer {token}'},
        json=collection.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.OK

    response = client.get(
        f'/collection/{collection.collection_id}/',
        headers={'Authorization': f'Bearer {token}'},
    )
    response = response.json()
    assert response['name'] == 'Novo Nome da Coleção'
    assert response['description'] == 'Nova descrição.'


@pytest.mark.asyncio
async def test_post_collection_entry(
    client, create_user, get_token, create_collection
):
    user = await create_user()
    token = get_token(user)
    collection = await create_collection(user=user)

    entry = {
        'collection_id': str(collection.collection_id),
        'entry_id': str(uuid4()),
        'type': 'XPTO',
    }

    response = client.post(
        '/collection/entry/',
        headers={'Authorization': f'Bearer {token}'},
        json=entry,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert collection_models.CollectionEntry(**response.json())
