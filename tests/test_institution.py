import io
from http import HTTPStatus
from pathlib import Path

import pytest

from simcc.schemas import institution_model
from tests.factories import institution_factory


@pytest.mark.asyncio
async def test_post_institution(
    client, create_admin_user, login_and_set_cookie
):
    institution = institution_factory.CreateInstitutionFactory()
    admin_user = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin_user)

    response = authenticated_client.post(
        '/institution/',
        json=institution.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.CREATED
    assert institution_model.Institution(**response.json())


@pytest.mark.asyncio
async def test_post_institution_list(
    client, create_admin_user, login_and_set_cookie
):
    AMONG = 3
    institutions = [
        institution_factory.CreateInstitutionFactory() for _ in range(AMONG)
    ]
    institutions_json = [i.model_dump(mode='json') for i in institutions]
    admin_user = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin_user)

    response = authenticated_client.post(
        '/institution/',
        json=institutions_json,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert len(response.json()) == AMONG


# WIP - Proteger as rotas
# @pytest.mark.asyncio
# async def test_post_institution_forbidden(
#     client, create_user, login_and_set_cookie
# ):
#     institution = institution_factory.CreateInstitutionFactory()
#     user = await create_user()
#     authenticated_client = login_and_set_cookie(user)

#     response = authenticated_client.post(
#         '/institution/',
#         json=institution.model_dump(mode='json'),
#     )

#     assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_get_institution(client, create_institution):
    # This endpoint is public, so no authentication is needed. No changes required.
    institution = await create_institution()
    get_response = client.get(f'/institution/{institution.institution_id}/')
    assert get_response.status_code == HTTPStatus.OK
    assert institution_model.Institution(**get_response.json())


@pytest.mark.asyncio
async def test_put_institution(
    client,
    create_institution,
    create_admin_user,
    login_and_set_cookie,
):
    inst = await create_institution()
    admin_user = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin_user)

    inst.name = 'Updated Institution Name'

    response = authenticated_client.put(
        '/institution/',
        json=inst.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['name'] == 'Updated Institution Name'
    assert response.json()['updated_at'] is not None


@pytest.mark.asyncio
async def test_delete_institution(
    client, create_admin_user, login_and_set_cookie
):
    institution = institution_factory.CreateInstitutionFactory()
    admin_user = await create_admin_user()
    authenticated_client = login_and_set_cookie(admin_user)

    post_response = authenticated_client.post(
        '/institution/',
        json=institution.model_dump(mode='json'),
    )
    inst = institution_model.Institution(**post_response.json())

    delete_response = authenticated_client.delete(
        f'/institution/{inst.institution_id}/',
    )

    assert delete_response.status_code == HTTPStatus.NO_CONTENT

    # Verify that the institution is gone (this is a public endpoint)
    get_response = client.get(f'/institution/{inst.institution_id}/')
    assert get_response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_upload_institution_icon(create_institution, client):
    """Testa o upload de uma imagem de ícone para uma instituição."""
    institution = await create_institution()
    file_content = b'fake image content'
    file_name = 'test_image.png'

    response = client.post(
        f'/institution/upload/{institution.institution_id}/icon',
        files={'file': (file_name, io.BytesIO(file_content), 'image/png')},
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    file_name_from_response = Path(data['path']).name
    upload_dir = Path('simcc/storage/upload')
    final_path = upload_dir / file_name_from_response
    assert final_path.is_file()


@pytest.mark.asyncio
async def test_delete_institution_icon(create_institution, client):
    """Testa a exclusão de uma imagem de ícone de uma instituição."""
    institution = await create_institution()
    upload_response = client.post(
        f'/institution/upload/{institution.institution_id}/icon',
        files={
            'file': (
                'image_to_delete.png',
                io.BytesIO(b'content'),
                'image/png',
            )
        },
    )
    assert upload_response.status_code == HTTPStatus.CREATED

    data = upload_response.json()
    uploaded_path = Path(data['path'])
    physical_file_path = Path('simcc/storage/upload') / uploaded_path.name
    assert physical_file_path.exists()

    delete_response = client.delete(
        f'/institution/upload/{institution.institution_id}/icon'
    )

    assert delete_response.status_code == HTTPStatus.OK
    assert delete_response.json()['message'] == 'Ícone excluído com sucesso.'
    assert not physical_file_path.exists()


@pytest.mark.asyncio
async def test_delete_institution_icon_not_found(create_institution, client):
    """Testa a tentativa de exclusão quando a instituição não tem ícone."""
    institution = await create_institution()

    response = client.delete(
        f'/institution/upload/{institution.institution_id}/icon'
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_upload_institution_cover(create_institution, client):
    """Testa o upload de uma imagem de capa para uma instituição."""
    institution = await create_institution()
    file_content = b'fake background content'
    file_name = 'background.jpg'

    response = client.post(
        f'/institution/upload/{institution.institution_id}/cover',
        files={'file': (file_name, io.BytesIO(file_content), 'image/jpeg')},
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    file_name_from_response = Path(data['path']).name
    final_path = Path('simcc/storage/upload') / file_name_from_response
    assert final_path.is_file()


@pytest.mark.asyncio
async def test_upload_institution_cover_replaces_old_one(
    create_institution, client
):
    """Testa se o upload de uma nova capa substitui a antiga."""
    institution = await create_institution()

    first_response = client.post(
        f'/institution/upload/{institution.institution_id}/cover',
        files={'file': ('first.png', io.BytesIO(b'first'), 'image/png')},
    )
    assert first_response.status_code == HTTPStatus.CREATED
    old_path = Path(first_response.json()['path'])
    old_physical_path = Path('simcc/storage/upload') / old_path.name
    assert old_physical_path.exists()

    second_response = client.post(
        f'/institution/upload/{institution.institution_id}/cover',
        files={'file': ('second.png', io.BytesIO(b'second'), 'image/png')},
    )

    assert second_response.status_code == HTTPStatus.CREATED
    new_path = Path(second_response.json()['path'])
    new_physical_path = Path('simcc/storage/upload') / new_path.name

    assert new_physical_path.exists()
    assert not old_physical_path.exists()


@pytest.mark.asyncio
async def test_delete_institution_cover(create_institution, client):
    """Testa a exclusão de uma imagem de capa de uma instituição."""
    institution = await create_institution()

    upload_response = client.post(
        f'/institution/upload/{institution.institution_id}/cover',
        files={
            'file': ('bg_to_delete.png', io.BytesIO(b'content'), 'image/png')
        },
    )
    assert upload_response.status_code == HTTPStatus.CREATED

    data = upload_response.json()
    physical_file_path = Path('simcc/storage/upload') / Path(data['path']).name
    assert physical_file_path.exists()

    delete_response = client.delete(
        f'/institution/upload/{institution.institution_id}/cover'
    )

    assert delete_response.status_code == HTTPStatus.OK
    assert (
        delete_response.json()['message']
        == 'Imagem de capa excluída com sucesso.'
    )
    assert not physical_file_path.exists()


@pytest.mark.asyncio
async def test_delete_institution_cover_not_found(create_institution, client):
    """Testa a tentativa de exclusão de uma capa inexistente."""
    institution = await create_institution()

    response = client.delete(
        f'/institution/upload/{institution.institution_id}/cover'
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
