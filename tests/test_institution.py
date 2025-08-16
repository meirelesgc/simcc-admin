from http import HTTPStatus

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


# WIP - Proteger as rotas
# @pytest.mark.asyncio
# async def test_put_institution_forbidden(
#     client, create_user, create_institution, login_and_set_cookie
# ):
#     user = await create_user()
#     inst = await create_institution()
#     authenticated_client = login_and_set_cookie(user)

#     inst.name = 'Attempted Update'

#     response = authenticated_client.put(
#         '/institution/',
#         json=inst.model_dump(mode='json'),
#     )

#     assert response.status_code == HTTPStatus.FORBIDDEN


# @pytest.mark.asyncio
# async def test_delete_institution_forbidden(
#     client, create_user, create_institution, login_and_set_cookie
# ):
#     user = await create_user()
#     institution = await create_institution()
#     authenticated_client = login_and_set_cookie(user)

#     response = authenticated_client.delete(
#         f'/institution/{institution.institution_id}/',
#     )

#     assert response.status_code == HTTPStatus.FORBIDDEN
