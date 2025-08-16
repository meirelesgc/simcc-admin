from http import HTTPStatus

import pytest

from simcc.schemas import researcher_model
from tests.factories import researcher_factory


@pytest.mark.asyncio
async def test_post_researcher(client, create_institution):
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
    auth_header,
):
    user = await create_admin_user()

    institution = await create_institution()
    researcher = await create_researcher(institution=institution)
    researcher.name = 'updated name'

    response = client.put(
        '/researcher/',
        headers=auth_header(user),
        json=researcher.model_dump(mode='json'),
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_delete_researcher(
    client, create_researcher, create_institution
):
    institution = await create_institution()
    researcher = await create_researcher(institution=institution)
    response = client.delete(f'/researcher/{researcher.researcher_id}/')
    assert response.status_code == HTTPStatus.NO_CONTENT
    response = client.get('/researcher/')
    assert len(response.json()) == 0
