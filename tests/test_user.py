import io
from http import HTTPStatus
from pathlib import Path

import pytest

from tests.factories import user_factory


@pytest.mark.asyncio
async def test_post_user(client, conn):
    EXPECTED_COUNT = 1
    user = user_factory.UserFactory()
    response = client.post('/user/', json=user.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.CREATED
    COUNT = await conn.select('SELECT COUNT(*) FROM users', one=True)
    assert COUNT.get('count') == EXPECTED_COUNT


def test_get_users_unauthorized(client):
    response = client.get('/user/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_users_forbidden_to_default_user(
    client, create_user, login_and_set_cookie
):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    response = authenticated_client.get('/user/')
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_get_users_as_admin(
    client, create_user, create_admin_user, login_and_set_cookie
):
    EXPECTED_COUNT = 2
    await create_user()
    admin = await create_admin_user()

    authenticated_client = login_and_set_cookie(admin)
    response = authenticated_client.get('/user/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == EXPECTED_COUNT


@pytest.mark.asyncio
async def test_get_single_user(client, create_user, login_and_set_cookie):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    response = authenticated_client.get(f'/user/{user.user_id}/')
    assert response.status_code == HTTPStatus.OK
    assert response.json().get('user_id') == str(user.user_id)


@pytest.mark.asyncio
async def test_get_single_user_by_admin(
    client, create_user, create_admin_user, login_and_set_cookie
):
    user = await create_user()
    admin = await create_admin_user()

    authenticated_client = login_and_set_cookie(admin)
    response = authenticated_client.get(f'/user/{user.user_id}/')
    assert response.status_code == HTTPStatus.OK
    assert response.json().get('user_id') == str(user.user_id)


@pytest.mark.asyncio
async def test_get_me(client, create_user, login_and_set_cookie):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    response = authenticated_client.get('/user/my-self/')
    assert response.status_code == HTTPStatus.OK
    assert response.json().get('user_id') == str(user.user_id)


@pytest.mark.asyncio
async def test_put_my_user(client, create_user, login_and_set_cookie):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    user.username = 'updated name'
    response = authenticated_client.put(
        '/user/',
        json=user.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json().get('username') == 'updated name'
    assert response.json().get('updated_at')


@pytest.mark.asyncio
async def test_put_user_by_other_user_forbidden(
    client, create_user, login_and_set_cookie
):
    user = await create_user()
    other_user = await create_user()

    authenticated_client = login_and_set_cookie(other_user)

    user.username = 'unauthorized update'
    response = authenticated_client.put(
        '/user/',
        json=user.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_put_user_by_admin(
    client, create_user, create_admin_user, login_and_set_cookie
):
    user = await create_user()
    admin = await create_admin_user()

    authenticated_client = login_and_set_cookie(admin)

    user.username = 'admin update'
    response = authenticated_client.put(
        '/user/',
        json=user.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json().get('username') == 'admin update'


@pytest.mark.asyncio
async def test_put_user_not_authenticated(client, create_user):
    user = await create_user()
    user.username = 'unauthenticated update'

    # Não define o cookie de autenticação no cliente.
    response = client.put(
        '/user/',
        json=user.model_dump(mode='json'),
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_single_user_forbidden(
    client, create_user, login_and_set_cookie
):
    user_one = await create_user()
    user_two = await create_user()

    authenticated_client = login_and_set_cookie(user_one)

    response = authenticated_client.get(f'/user/{user_two.user_id}/')

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_delete_user_forbidden(
    client, create_user, login_and_set_cookie
):
    user_one = await create_user()
    user_two = await create_user()

    authenticated_client = login_and_set_cookie(user_one)

    response = authenticated_client.delete(f'/user/{user_two.user_id}/')

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_delete_user(client, create_user, login_and_set_cookie):
    user = await create_user()
    authenticated_client = login_and_set_cookie(user)
    response = authenticated_client.delete(f'/user/{user.user_id}/')

    assert response.status_code == HTTPStatus.NO_CONTENT

    response = authenticated_client.get(f'/user/{user.user_id}/')
    assert response.status_code == HTTPStatus.FORBIDDEN or HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_upload_icon(create_user, login_and_set_cookie):
    """Testa o upload de uma imagem de ícone para o usuário."""
    user = await create_user()
    client = login_and_set_cookie(user)
    file_content = b'fake image content'
    file_name = 'test_image.png'

    response = client.post(
        '/user/upload/icon',
        files={'file': (file_name, io.BytesIO(file_content), 'image/png')},
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    file_name_from_response = Path(data['path']).name
    upload_dir = Path('simcc/storage/upload')
    final_path = upload_dir / file_name_from_response
    assert final_path.is_file()


@pytest.mark.asyncio
async def test_delete_icon(create_user, login_and_set_cookie):
    """Testa a exclusão de uma imagem de ícone do usuário."""
    user = await create_user()
    client = login_and_set_cookie(user)

    upload_response = client.post(
        '/user/upload/icon',
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

    delete_response = client.delete('/user/upload/icon')

    assert delete_response.status_code == HTTPStatus.OK
    assert delete_response.json()['message'] == 'Ícone excluído com sucesso.'
    assert not physical_file_path.exists()


@pytest.mark.asyncio
async def test_delete_icon_not_found(create_user, login_and_set_cookie):
    """Testa a tentativa de exclusão quando não há ícone."""
    user = await create_user()
    client = login_and_set_cookie(user)

    response = client.delete('/user/upload/icon')

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_upload_cover(create_user, login_and_set_cookie):
    """Testa o upload de uma imagem de capa para o usuário."""
    user = await create_user()
    client = login_and_set_cookie(user)
    file_content = b'fake background content'
    file_name = 'background.jpg'

    response = client.post(
        '/user/upload/cover',
        files={'file': (file_name, io.BytesIO(file_content), 'image/jpeg')},
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    file_name_from_response = Path(data['path']).name
    final_path = Path('simcc/storage/upload') / file_name_from_response
    assert final_path.is_file()


@pytest.mark.asyncio
async def test_upload_cover_replaces_old_one(
    create_user, login_and_set_cookie
):
    """Testa se o upload de uma nova capa substitui a antiga."""
    user = await create_user()
    client = login_and_set_cookie(user)

    first_response = client.post(
        '/user/upload/cover',
        files={'file': ('first.png', io.BytesIO(b'first'), 'image/png')},
    )
    assert first_response.status_code == HTTPStatus.CREATED
    old_path = Path(first_response.json()['path'])
    old_physical_path = Path('simcc/storage/upload') / old_path.name
    assert old_physical_path.exists()

    second_response = client.post(
        '/user/upload/cover',
        files={'file': ('second.png', io.BytesIO(b'second'), 'image/png')},
    )

    assert second_response.status_code == HTTPStatus.CREATED
    new_path = Path(second_response.json()['path'])
    new_physical_path = Path('simcc/storage/upload') / new_path.name

    assert new_physical_path.exists()
    assert not old_physical_path.exists()


@pytest.mark.asyncio
async def test_delete_cover(create_user, login_and_set_cookie):
    """Testa a exclusão de uma imagem de capa."""
    user = await create_user()
    client = login_and_set_cookie(user)

    upload_response = client.post(
        '/user/upload/cover',
        files={
            'file': ('bg_to_delete.png', io.BytesIO(b'content'), 'image/png')
        },
    )
    assert upload_response.status_code == HTTPStatus.CREATED

    data = upload_response.json()
    physical_file_path = Path('simcc/storage/upload') / Path(data['path']).name
    assert physical_file_path.exists()

    delete_response = client.delete('/user/upload/cover')

    assert delete_response.status_code == HTTPStatus.OK
    assert (
        delete_response.json()['message']
        == 'Imagem de capa excluída com sucesso.'
    )
    assert not physical_file_path.exists()


@pytest.mark.asyncio
async def test_delete_cover_not_found(create_user, login_and_set_cookie):
    """Testa a tentativa de exclusão de uma capa inexistente."""
    user = await create_user()
    client = login_and_set_cookie(user)

    response = client.delete('/user/upload/cover')

    assert response.status_code == HTTPStatus.NOT_FOUND
