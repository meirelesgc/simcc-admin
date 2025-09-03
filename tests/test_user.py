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
async def test_upload_profile_image(create_user, login_and_set_cookie):
    user = await create_user()
    client = login_and_set_cookie(user)
    file_content = b'fake image content'
    file_name = 'test_image.png'

    response = client.post(
        '/user/upload/profile_image',
        files={'file': (file_name, io.BytesIO(file_content), 'image/png')},
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    file_name_from_response = Path(data['path']).name
    upload_dir = Path('simcc/storage/upload')
    final_path = upload_dir / file_name_from_response
    assert final_path.is_file()


@pytest.mark.asyncio
async def test_delete_profile_image(create_user, login_and_set_cookie):
    user = await create_user()
    client = login_and_set_cookie(user)

    upload_response = client.post(
        '/user/upload/profile_image',
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

    # Act: Envia a requisição para deletar a imagem
    delete_response = client.delete('/user/upload/profile_image')

    # Assert: Verifica se a operação foi bem-sucedida
    assert delete_response.status_code == HTTPStatus.OK
    assert (
        delete_response.json()['message']
        == 'Imagem de perfil excluída com sucesso.'
    )
    assert (
        not physical_file_path.exists()
    )  # Garante que o arquivo físico foi removido


@pytest.mark.asyncio
async def test_delete_profile_image_not_found(
    create_user, login_and_set_cookie
):
    # Arrange: Cria um usuário sem imagem de perfil
    user = await create_user()
    client = login_and_set_cookie(user)

    # Act
    response = client.delete('/user/upload/profile_image')

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_upload_background_image(create_user, login_and_set_cookie):
    # Arrange
    user = await create_user()
    client = login_and_set_cookie(user)
    file_content = b'fake background content'
    file_name = 'background.jpg'

    # Act
    response = client.post(
        '/user/upload/background_image',
        files={'file': (file_name, io.BytesIO(file_content), 'image/jpeg')},
    )

    # Assert
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    file_name_from_response = Path(data['path']).name
    final_path = Path('simcc/storage/upload') / file_name_from_response
    assert final_path.is_file()


@pytest.mark.asyncio
async def test_upload_background_image_replaces_old_one(
    create_user, login_and_set_cookie
):
    # Arrange: Faz o upload de uma primeira imagem
    user = await create_user()
    client = login_and_set_cookie(user)

    first_response = client.post(
        '/user/upload/background_image',
        files={'file': ('first.png', io.BytesIO(b'first'), 'image/png')},
    )
    assert first_response.status_code == HTTPStatus.CREATED
    old_path = Path(first_response.json()['path'])
    old_physical_path = Path('simcc/storage/upload') / old_path.name
    assert old_physical_path.exists()

    # Act: Faz o upload de uma segunda imagem
    second_response = client.post(
        '/user/upload/background_image',
        files={'file': ('second.png', io.BytesIO(b'second'), 'image/png')},
    )

    # Assert: Verifica se a nova imagem existe e a antiga foi removida
    assert second_response.status_code == HTTPStatus.CREATED
    new_path = Path(second_response.json()['path'])
    new_physical_path = Path('simcc/storage/upload') / new_path.name

    assert new_physical_path.exists()
    assert not old_physical_path.exists()


@pytest.mark.asyncio
async def test_delete_background_image(create_user, login_and_set_cookie):
    # Arrange: Cria um usuário e faz o upload de uma imagem de fundo
    user = await create_user()
    client = login_and_set_cookie(user)

    upload_response = client.post(
        '/user/upload/background_image',
        files={
            'file': ('bg_to_delete.png', io.BytesIO(b'content'), 'image/png')
        },
    )
    assert upload_response.status_code == HTTPStatus.CREATED

    data = upload_response.json()
    physical_file_path = Path('simcc/storage/upload') / Path(data['path']).name
    assert physical_file_path.exists()

    # Act: Envia a requisição para deletar
    delete_response = client.delete('/user/upload/background_image')

    # Assert
    assert delete_response.status_code == HTTPStatus.OK
    assert (
        delete_response.json()['message']
        == 'Imagem de fundo excluída com sucesso.'
    )
    assert not physical_file_path.exists()


@pytest.mark.asyncio
async def test_delete_background_image_not_found(
    create_user, login_and_set_cookie
):
    # Arrange: Cria um usuário sem imagem de fundo
    user = await create_user()
    client = login_and_set_cookie(user)

    # Act
    response = client.delete('/user/upload/background_image')

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
