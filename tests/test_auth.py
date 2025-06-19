from http import HTTPStatus


def test_orcid_redirect(client):
    response = client.get('/auth/orcid/login', follow_redirects=False)
    assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
    assert 'location' in response.headers
    assert response.headers['location'].startswith(
        'https://orcid.org/oauth/authorize'
    )
