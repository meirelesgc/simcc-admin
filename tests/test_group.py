from http import HTTPStatus

import pytest

from simcc.schemas import group_schemas
from tests.factories import group_factory

pytestmark = pytest.mark.asyncio


async def test_create_group(
    client, create_admin_user, login_and_set_cookie, create_institution
):
    admin_user = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin_user)

    group_data = group_factory.GroupFactory.build()

    response = authenticated_client.post(
        '/group/',
        json=group_data.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.CREATED

    created_group = group_schemas.GroupPublic(**response.json())
    assert created_group.name == group_data.name
    assert created_group.group_identifier == group_data.group_identifier


async def test_list_groups(
    client,
    create_admin_user,
    login_and_set_cookie,
    create_group,
    create_institution,
):
    admin_user = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin_user)

    await create_group()
    await create_group()

    response = authenticated_client.get('/group/')

    assert response.status_code == HTTPStatus.OK

    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 2


async def test_update_group(
    client,
    create_admin_user,
    login_and_set_cookie,
    create_group,
    create_institution,
):
    admin_user = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin_user)

    existing_group = await create_group()

    new_name = 'Grupo de Pesquisa Atualizado em IA'
    update_data = {
        'id': str(existing_group['id']),
        'name': new_name,
        'group_identifier': existing_group['group_identifier'],
    }

    response = authenticated_client.put(
        '/group/',
        json=update_data,
    )
    print(response.json())
    assert response.status_code == HTTPStatus.OK

    updated_group = group_schemas.GroupPublic(**response.json())
    assert updated_group.name == new_name
    assert updated_group.id == existing_group['id']


async def test_delete_group(
    client,
    create_admin_user,
    login_and_set_cookie,
    create_group,
    create_institution,
):
    """
    Testa a exclusão de um grupo.
    """
    admin_user = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin_user)

    group_to_delete = await create_group()
    group_id = group_to_delete['id']

    response = authenticated_client.delete(f'/group/{group_id}')

    assert response.status_code == HTTPStatus.NO_CONTENT
    get_response = authenticated_client.get(f'/group/{group_id}')
    assert get_response.status_code == HTTPStatus.NOT_FOUND


import io
import os
from pathlib import Path

import pytest

UPLOAD_DIR = 'simcc/storage/upload'


@pytest.mark.asyncio
async def test_upload_icon_for_group(create_group, client):
    """Testa o upload de um ícone para um grupo de pesquisa."""
    group = await create_group()
    file_content = b'fake icon content'
    file_name = 'test_icon.png'

    response = client.post(
        f'/group/upload/{group["id"]}/icon',
        files={'file': (file_name, io.BytesIO(file_content), 'image/png')},
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    file_name_from_response = Path(data['path']).name
    final_path = Path(UPLOAD_DIR) / file_name_from_response
    assert final_path.is_file()
    os.remove(final_path)


@pytest.mark.asyncio
async def test_delete_icon_for_group(create_group, client):
    """Testa a exclusão de um ícone de um grupo de pesquisa."""
    group = await create_group()
    upload_response = client.post(
        f'/group/upload/{group["id"]}/icon',
        files={
            'file': (
                'icon_to_delete.png',
                io.BytesIO(b'content'),
                'image/png',
            )
        },
    )
    assert upload_response.status_code == HTTPStatus.CREATED

    data = upload_response.json()
    uploaded_path = Path(data['path'])
    physical_file_path = Path(UPLOAD_DIR) / uploaded_path.name
    assert physical_file_path.exists()

    delete_response = client.delete(f'/group/upload/{group["id"]}/icon')
    assert delete_response.status_code == HTTPStatus.OK
    assert delete_response.json()['message'] == 'Ícone excluído com sucesso.'
    assert not physical_file_path.exists()


@pytest.mark.asyncio
async def test_delete_icon_not_found_for_group(create_group, client):
    """Testa a tentativa de exclusão de ícone inexistente para um grupo."""
    group = await create_group()
    response = client.delete(f'/group/upload/{group["id"]}/icon')
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_upload_cover_for_group(create_group, client):
    """Testa o upload de uma capa para um grupo de pesquisa."""
    group = await create_group()
    file_content = b'fake background content'
    file_name = 'background.jpg'

    response = client.post(
        f'/group/upload/{group["id"]}/cover',
        files={'file': (file_name, io.BytesIO(file_content), 'image/jpeg')},
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    file_name_from_response = Path(data['path']).name
    final_path = Path(UPLOAD_DIR) / file_name_from_response
    assert final_path.is_file()
    os.remove(final_path)


@pytest.mark.asyncio
async def test_upload_cover_replaces_old_one_for_group(create_group, client):
    """Testa se o upload de uma nova capa substitui a antiga para um grupo de pesquisa."""
    group = await create_group()
    first_response = client.post(
        f'/group/upload/{group["id"]}/cover',
        files={'file': ('first.png', io.BytesIO(b'first'), 'image/png')},
    )
    assert first_response.status_code == HTTPStatus.CREATED
    old_path = Path(first_response.json()['path'])
    old_physical_path = Path(UPLOAD_DIR) / old_path.name
    assert old_physical_path.exists()

    second_response = client.post(
        f'/group/upload/{group["id"]}/cover',
        files={'file': ('second.png', io.BytesIO(b'second'), 'image/png')},
    )

    assert second_response.status_code == HTTPStatus.CREATED
    new_path = Path(second_response.json()['path'])
    new_physical_path = Path(UPLOAD_DIR) / new_path.name

    assert new_physical_path.exists()
    assert not old_physical_path.exists()

    os.remove(new_physical_path)


@pytest.mark.asyncio
async def test_delete_cover_for_group(create_group, client):
    """Testa a exclusão de uma capa para um grupo de pesquisa."""
    group = await create_group()
    upload_response = client.post(
        f'/group/upload/{group["id"]}/cover',
        files={
            'file': ('bg_to_delete.png', io.BytesIO(b'content'), 'image/png')
        },
    )
    assert upload_response.status_code == HTTPStatus.CREATED

    data = upload_response.json()
    physical_file_path = Path(UPLOAD_DIR) / Path(data['path']).name
    assert physical_file_path.exists()

    delete_response = client.delete(f'/group/upload/{group["id"]}/cover')
    assert delete_response.status_code == HTTPStatus.OK
    assert (
        delete_response.json()['message']
        == 'Imagem de capa excluída com sucesso.'
    )
    assert not physical_file_path.exists()


@pytest.mark.asyncio
async def test_delete_cover_not_found_for_group(create_group, client):
    """Testa a tentativa de exclusão de uma capa inexistente para um grupo."""
    group = await create_group()
    response = client.delete(f'/group/upload/{group["id"]}/cover')
    assert response.status_code == HTTPStatus.NOT_FOUND
