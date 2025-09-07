import io
import os
from http import HTTPStatus
from pathlib import Path

import pytest

# Supondo que `client` e `create_program` sejam fixtures disponíveis
# create_program deve retornar um programa de pós-graduação criado no banco de dados.

UPLOAD_DIR = 'simcc/storage/upload'


@pytest.mark.asyncio
async def test_upload_icon_for_program(create_program, client):
    """Testa o upload de um ícone para um programa de pós-graduação."""
    program = await create_program()
    file_content = b'fake icon content'
    file_name = 'test_icon.png'

    response = client.post(
        f'/graduate-program/upload/{program["graduate_program_id"]}/icon',
        files={'file': (file_name, io.BytesIO(file_content), 'image/png')},
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    file_name_from_response = Path(data['path']).name
    final_path = Path(UPLOAD_DIR) / file_name_from_response
    assert final_path.is_file()
    os.remove(final_path)


@pytest.mark.asyncio
async def test_delete_icon_for_program(create_program, client):
    """Testa a exclusão de um ícone de um programa de pós-graduação."""
    program = await create_program()
    upload_response = client.post(
        f'/graduate-program/upload/{program["graduate_program_id"]}/icon',
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

    delete_response = client.delete(
        f'/graduate-program/upload/{program["graduate_program_id"]}/icon'
    )
    assert delete_response.status_code == HTTPStatus.OK
    assert delete_response.json()['message'] == 'Ícone excluído com sucesso.'
    assert not physical_file_path.exists()


@pytest.mark.asyncio
async def test_delete_icon_not_found_for_program(create_program, client):
    """Testa a tentativa de exclusão de ícone inexistente para um programa."""
    program = await create_program()
    response = client.delete(
        f'/graduate-program/upload/{program["graduate_program_id"]}/icon'
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_upload_cover_for_program(create_program, client):
    """Testa o upload de uma capa para um programa de pós-graduação."""
    program = await create_program()
    file_content = b'fake background content'
    file_name = 'background.jpg'

    response = client.post(
        f'/graduate-program/upload/{program["graduate_program_id"]}/cover',
        files={'file': (file_name, io.BytesIO(file_content), 'image/jpeg')},
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    file_name_from_response = Path(data['path']).name
    final_path = Path(UPLOAD_DIR) / file_name_from_response
    assert final_path.is_file()
    os.remove(final_path)


@pytest.mark.asyncio
async def test_upload_cover_replaces_old_one_for_program(
    create_program, client
):
    """Testa se o upload de uma nova capa substitui a antiga para um programa."""
    program = await create_program()
    first_response = client.post(
        f'/graduate-program/upload/{program["graduate_program_id"]}/cover',
        files={'file': ('first.png', io.BytesIO(b'first'), 'image/png')},
    )
    assert first_response.status_code == HTTPStatus.CREATED
    old_path = Path(first_response.json()['path'])
    old_physical_path = Path(UPLOAD_DIR) / old_path.name
    assert old_physical_path.exists()

    second_response = client.post(
        f'/graduate-program/upload/{program["graduate_program_id"]}/cover',
        files={'file': ('second.png', io.BytesIO(b'second'), 'image/png')},
    )

    assert second_response.status_code == HTTPStatus.CREATED
    new_path = Path(second_response.json()['path'])
    new_physical_path = Path(UPLOAD_DIR) / new_path.name

    assert new_physical_path.exists()
    assert not old_physical_path.exists()

    os.remove(new_physical_path)


@pytest.mark.asyncio
async def test_delete_cover_for_program(create_program, client):
    """Testa a exclusão de uma capa para um programa de pós-graduação."""
    program = await create_program()
    upload_response = client.post(
        f'/graduate-program/upload/{program["graduate_program_id"]}/cover',
        files={
            'file': ('bg_to_delete.png', io.BytesIO(b'content'), 'image/png')
        },
    )
    assert upload_response.status_code == HTTPStatus.CREATED

    data = upload_response.json()
    physical_file_path = Path(UPLOAD_DIR) / Path(data['path']).name
    assert physical_file_path.exists()

    delete_response = client.delete(
        f'/graduate-program/upload/{program["graduate_program_id"]}/cover'
    )
    assert delete_response.status_code == HTTPStatus.OK
    assert (
        delete_response.json()['message']
        == 'Imagem de capa excluída com sucesso.'
    )
    assert not physical_file_path.exists()


@pytest.mark.asyncio
async def test_delete_cover_not_found_for_program(create_program, client):
    """Testa a tentativa de exclusão de uma capa inexistente para um programa."""
    program = await create_program()
    response = client.delete(
        f'/graduate-program/upload/{program["graduate_program_id"]}/cover'
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
