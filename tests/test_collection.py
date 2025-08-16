from http import HTTPStatus
from uuid import uuid4

import pytest

from simcc.schemas.features import collection_models
from tests.factories.features import collection_factory


@pytest.mark.asyncio
async def test_post_collection(client, create_user, login_and_set_cookie):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    collection = collection_factory.CreateCollectionFactory()

    response = authenticated_client.post(
        '/collection/',
        json=collection.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.CREATED
    assert collection_models.CreateCollection(**response.json())


@pytest.mark.asyncio
async def test_get_collections(
    client, create_user, login_and_set_cookie, create_collection
):
    AMONG = 2
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    for _ in range(AMONG):
        await create_collection(user=user)

    response = authenticated_client.get('/collection/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == AMONG


@pytest.mark.asyncio
async def test_get_collection_by_id(
    client, create_user, login_and_set_cookie, create_collection
):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    collection = await create_collection(user)

    response = authenticated_client.get(
        f'/collection/{collection.collection_id}/'
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['collection_id'] == str(collection.collection_id)


@pytest.mark.asyncio
async def test_get_public_collections(
    client, create_user, create_collection, login_and_set_cookie
):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    collection = await create_collection(user)

    # Public endpoint, no auth needed
    response = client.get(f'/collection/public/{user.user_id}/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 0

    collection.visible = True
    # Authenticated request to update the collection
    authenticated_client.put(
        '/collection/',
        json=collection.model_dump(mode='json'),
    )

    # Public endpoint again, should now find one
    response = client.get(f'/collection/public/{user.user_id}/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_delete_collection(
    client, create_user, login_and_set_cookie, create_collection
):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    collection = await create_collection(user)

    response = authenticated_client.delete(
        f'/collection/{collection.collection_id}/'
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = authenticated_client.get('/collection/')
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_get_collection_by_id_not_found(
    client, create_user, login_and_set_cookie
):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    non_existent_id = uuid4()

    response = authenticated_client.get(f'/collection/{non_existent_id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_update_collection(
    client, create_user, login_and_set_cookie, create_collection
):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    collection = await create_collection(user=user)

    collection.name = 'Novo Nome da Coleção'
    collection.description = 'Nova descrição.'
    collection.visible = False

    authenticated_client.put(
        '/collection/',
        json=collection.model_dump(mode='json'),
    )

    response = authenticated_client.get(
        f'/collection/{collection.collection_id}/'
    )
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['name'] == 'Novo Nome da Coleção'
    assert response_data['description'] == 'Nova descrição.'


@pytest.mark.asyncio
async def test_post_entry_to_collection(
    client, create_user, login_and_set_cookie, create_collection
):
    owner = await create_user()
    authenticated_client = login_and_set_cookie(owner)
    collection = await create_collection(user=owner)
    entry_data = collection_factory.CreateCollectionEntryFactory()

    response = authenticated_client.post(
        f'/collection/{collection.collection_id}/entries/',
        json=entry_data.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.CREATED
    response_data = response.json()
    assert response_data['entry_id'] == str(entry_data.entry_id)
    assert response_data['collection_id'] == str(collection.collection_id)
    assert response_data['type'] == entry_data.type


@pytest.mark.asyncio
async def test_get_entries_from_collection(
    client,
    create_user,
    login_and_set_cookie,
    create_collection,
    create_entry_in_collection,
):
    AMONG = 3
    owner = await create_user()
    authenticated_client = login_and_set_cookie(owner)
    collection = await create_collection(user=owner)
    for _ in range(AMONG):
        await create_entry_in_collection(collection, owner)

    response = authenticated_client.get(
        f'/collection/{collection.collection_id}/entries/'
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == AMONG


@pytest.mark.asyncio
async def test_delete_entry_from_collection(
    client,
    create_user,
    login_and_set_cookie,
    create_collection,
    create_entry_in_collection,
):
    owner = await create_user()
    authenticated_client = login_and_set_cookie(owner)
    collection = await create_collection(user=owner)
    entry = await create_entry_in_collection(collection, owner)

    delete_response = authenticated_client.delete(
        f'/collection/{collection.collection_id}/entries/{entry.entry_id}/'
    )
    assert delete_response.status_code == HTTPStatus.NO_CONTENT

    response = authenticated_client.get(
        f'/collection/{collection.collection_id}/entries/'
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_post_entry_permission_denied(
    client, create_user, login_and_set_cookie, create_collection
):
    owner = await create_user(username='dono')
    attacker = await create_user(username='atacante')
    attacker_client = login_and_set_cookie(attacker)
    collection = await create_collection(user=owner)
    entry_data = collection_factory.CreateCollectionEntryFactory()

    response = attacker_client.post(
        f'/collection/{collection.collection_id}/entries/',
        json=entry_data.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


# @pytest.mark.asyncio
# async def test_get_entries_permission_logic(
#     client,
#     create_user,
#     login_and_set_cookie,
#     create_collection,
#     create_entry_in_collection,
# ):
#     owner = await create_user(username='dono')
#     viewer = await create_user(username='visitante')

#     # Loga o dono
#     client.cookies.clear()
#     owner_client = login_and_set_cookie(owner)

#     # Loga o visitante
#     client.cookies.clear()
#     viewer_client = login_and_set_cookie(viewer)

#     private_collection = await create_collection(user=owner)
#     await create_entry_in_collection(private_collection, owner)

#     response_private = viewer_client.get(
#         f'/collection/{private_collection.collection_id}/entries/'
#     )
#     assert response_private.status_code == HTTPStatus.NOT_FOUND

#     public_collection = await create_collection(user=owner, visible=True)
#     owner_client.put(
#         '/collection/',
#         json=public_collection.model_dump(mode='json'),
#     )
#     await create_entry_in_collection(public_collection, owner)

#     response_public = viewer_client.get(
#         f'/collection/{public_collection.collection_id}/entries/'
#     )
#     assert response_public.status_code == HTTPStatus.OK
#     assert len(response_public.json()) == 1


# @pytest.mark.asyncio
# async def test_delete_entry_permission_denied(
#     client,
#     create_user,
#     login_and_set_cookie,
#     create_collection,
#     create_entry_in_collection,
# ):
#     owner = await create_user(username='dono')
#     attacker = await create_user(username='atacante')
#     attacker_client = login_and_set_cookie(attacker)
#     collection = await create_collection(user=owner)
#     entry = await create_entry_in_collection(collection, owner)

#     response = attacker_client.delete(
#         f'/collection/{collection.collection_id}/entries/{entry.entry_id}/'
#     )
#     assert response.status_code == HTTPStatus.NOT_FOUND
