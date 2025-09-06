import io
from http import HTTPStatus
from pathlib import Path
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


@pytest.mark.asyncio
async def test_upload_collection_cover(
    create_user, login_and_set_cookie, create_collection
):
    """Testa o upload de uma imagem de capa para uma coleção."""
    user = await create_user()
    client = login_and_set_cookie(user)
    collection = await create_collection(user=user)
    file_content = b'fake cover content'
    file_name = 'test_collection_cover.jpg'

    # Endpoint para upload de capa da coleção
    response = client.post(
        f'/collection/upload/{collection.collection_id}/cover',
        files={'file': (file_name, io.BytesIO(file_content), 'image/jpeg')},
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    file_name_from_response = Path(data['path']).name
    upload_dir = Path('simcc/storage/upload')
    final_path = upload_dir / file_name_from_response
    assert final_path.is_file()


@pytest.mark.asyncio
async def test_upload_collection_cover_replaces_old_one(
    create_user, login_and_set_cookie, create_collection
):
    """Testa se o upload de uma nova capa substitui a antiga."""
    user = await create_user()
    client = login_and_set_cookie(user)
    collection = await create_collection(user=user)

    # Faz o upload da primeira imagem de capa
    first_response = client.post(
        f'/collection/upload/{collection.collection_id}/cover',
        files={'file': ('first.png', io.BytesIO(b'first'), 'image/png')},
    )
    assert first_response.status_code == HTTPStatus.CREATED
    old_path = Path(first_response.json()['path'])
    old_physical_path = Path('simcc/storage/upload') / old_path.name
    assert old_physical_path.exists()

    # Faz o upload da segunda imagem de capa
    second_response = client.post(
        f'/collection/upload/{collection.collection_id}/cover',
        files={'file': ('second.png', io.BytesIO(b'second'), 'image/png')},
    )

    # Verifica se a nova imagem existe e a antiga foi removida
    assert second_response.status_code == HTTPStatus.CREATED
    new_path = Path(second_response.json()['path'])
    new_physical_path = Path('simcc/storage/upload') / new_path.name
    assert new_physical_path.exists()
    assert not old_physical_path.exists()


@pytest.mark.asyncio
async def test_delete_collection_cover(
    create_user, login_and_set_cookie, create_collection
):
    """Testa a exclusão de uma imagem de capa de uma coleção."""
    user = await create_user()
    client = login_and_set_cookie(user)
    collection = await create_collection(user=user)

    # Simula o upload da imagem de capa
    upload_response = client.post(
        f'/collection/upload/{collection.collection_id}/cover',
        files={
            'file': (
                'cover_to_delete.png',
                io.BytesIO(b'content'),
                'image/png',
            )
        },
    )
    assert upload_response.status_code == HTTPStatus.CREATED

    data = upload_response.json()
    physical_file_path = Path('simcc/storage/upload') / Path(data['path']).name
    assert physical_file_path.exists()

    # Endpoint para exclusão de capa da coleção
    delete_response = client.delete(
        f'/collection/upload/{collection.collection_id}/cover'
    )

    assert delete_response.status_code == HTTPStatus.OK
    assert (
        delete_response.json()['message']
        == 'Imagem de capa excluída com sucesso.'
    )
    assert not physical_file_path.exists()


@pytest.mark.asyncio
async def test_delete_collection_cover_not_found(
    create_user, login_and_set_cookie, create_collection
):
    """Testa a tentativa de exclusão de uma capa inexistente."""
    user = await create_user()
    client = login_and_set_cookie(user)
    collection = await create_collection(user=user)

    # Não faz o upload da imagem. Apenas tenta deletar.
    response = client.delete(
        f'/collection/upload/{collection.collection_id}/cover'
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
