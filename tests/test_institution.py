from http import HTTPStatus

import pytest

from simcc.schemas import institution_model
from tests.factories import institution_factory


@pytest.mark.asyncio
async def test_post_institution(client, create_admin_user, get_token):
    institution = institution_factory.CreateInstitutionFactory()
    admin_user = await create_admin_user()
    response = client.post(
        '/institution/',
        json=institution.model_dump(mode='json'),
        headers={'Authorization': f'Bearer {get_token(admin_user)}'},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert institution_model.Institution(**response.json())


@pytest.mark.asyncio
async def test_post_institution_list(client, create_admin_user, get_token):
    AMONG = 3
    institution = [institution_factory.CreateInstitutionFactory() for _ in range(AMONG)]  # fmt: skip  # noqa: E501
    institution = [i.model_dump(mode='json') for i in institution]
    admin_user = await create_admin_user()
    response = client.post(
        '/institution/',
        json=institution,
        headers={'Authorization': f'Bearer {get_token(admin_user)}'},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert len(response.json()) == AMONG


@pytest.mark.asyncio
async def _test_post_institution_forbidden(client, create_user, get_token):
    institution = institution_factory.CreateInstitutionFactory()
    user = await create_user()

    response = client.post(
        '/institution/',
        json=institution.model_dump(mode='json'),
        headers={'Authorization': f'Bearer {get_token(user)}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_get_institution(client, create_institution):
    institution = await create_institution()
    get_response = client.get(f'/institution/{institution.institution_id}/')
    assert get_response.status_code == HTTPStatus.OK
    assert institution_model.Institution(**get_response.json())


@pytest.mark.asyncio
async def test_put_institution(
    client,
    create_institution,
    create_admin_user,
    get_token,
):
    inst = await create_institution()
    admin_user = await create_admin_user()

    inst.name = 'Updated Institution Name'

    response = client.put(
        '/institution/',
        json=inst.model_dump(mode='json'),
        headers={'Authorization': f'Bearer {get_token(admin_user)}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['name'] == 'Updated Institution Name'
    assert response.json()['updated_at'] is not None


@pytest.mark.asyncio
async def test_delete_institution(client, create_admin_user, get_token):
    institution = institution_factory.CreateInstitutionFactory()
    admin_user = await create_admin_user()

    post_response = client.post(
        '/institution/',
        json=institution.model_dump(mode='json'),
        headers={'Authorization': f'Bearer {get_token(admin_user)}'},
    )
    inst = institution_model.Institution(**post_response.json())

    delete_response = client.delete(
        f'/institution/{inst.institution_id}/',
        headers={'Authorization': f'Bearer {get_token(admin_user)}'},
    )

    assert delete_response.status_code == HTTPStatus.NO_CONTENT

    get_response = client.get(f'/institution/{inst.institution_id}/')
    assert get_response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def _test_put_institution_forbidden(
    client, create_user, create_institution, get_token
):
    user = await create_user()
    inst = await create_institution()

    inst.name = 'Attempted Update'

    response = client.put(
        '/institution/',
        json=inst.model_dump(mode='json'),
        headers={'Authorization': f'Bearer {get_token(user)}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def _test_delete_institution_forbidden(
    client, create_user, create_institution, get_token
):
    user = await create_user()
    institution = await create_institution()

    response = client.delete(
        f'/institution/{institution.institution_id}/',
        headers={'Authorization': f'Bearer {get_token(user)}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
