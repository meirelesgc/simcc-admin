from http import HTTPStatus

import pytest

from simcc.schemas import researcher_model
from tests.factories import researcher_factory


@pytest.mark.asyncio
async def test_post_researcher(client, create_institution):
    """
    Tests creating a researcher. Assumes this is a public endpoint.
    No changes needed.
    """
    institution = await create_institution()
    researcher = researcher_factory.CreateResearcherFactory(
        institution_id=institution.institution_id,
    )

    response = client.post(
        '/researcher/',
        json=researcher.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.CREATED
    assert researcher_model.ResearcherResponse(**response.json())


@pytest.mark.asyncio
async def test_get_researchers(client, create_researcher, create_institution):
    """
    Tests listing researchers. Assumes this is a public endpoint.
    No changes needed.
    """
    institution = await create_institution()
    await create_researcher(institution=institution)
    response = client.get('/researcher/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_put_researchers(
    client,
    create_researcher,
    create_institution,
    create_admin_user,
    login_and_set_cookie,  # <-- Change fixture
):
    """
    Tests updating a researcher, requires admin authentication.
    """
    admin_user = await create_admin_user()
    # Create a client that is authenticated as the admin user
    authenticated_client = login_and_set_cookie(admin_user)

    institution = await create_institution()
    researcher = await create_researcher(institution=institution)
    researcher.name = 'updated name'

    # Use the authenticated client and remove the headers
    response = authenticated_client.put(
        '/researcher/',
        json=researcher.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_delete_researcher(
    client,
    create_researcher,
    create_institution,
    create_admin_user,
    login_and_set_cookie,  # <-- Add fixtures for authentication
):
    """
    Tests deleting a researcher, requires admin authentication.
    """
    admin_user = await create_admin_user()
    # Create a client that is authenticated as the admin user
    authenticated_client = login_and_set_cookie(admin_user)

    institution = await create_institution()
    researcher = await create_researcher(institution=institution)

    # Use the authenticated client for the delete operation
    response = authenticated_client.delete(
        f'/researcher/{researcher.researcher_id}/'
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    # Use a non-authenticated client to verify public access reflects the change
    response = client.get('/researcher/')
    assert len(response.json()) == 0
