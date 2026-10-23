import pytest

@pytest.mark.django_db
def test_user_registration(api_client):
    response = api_client.post(
        '/api/auth/register/',
        {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPassword123'
        },
        format = 'json'
    )
    assert response.status_code == 201
    assert response.data['message'] == 'User registered successfully'

@pytest.mark.django_db
def test_user_login(api_client, user):
    response = api_client.post(
        '/api/auth/login/',
        {
            'username': 'testuser',
            'password': 'TestPassword123'
        },
        format = 'json'
    )

    assert response.status_code ==201
    assert 'access' in response.data
    assert 'refresh' in response.data

@pytest.mark.django_db
def test_authenticated_profile(api_client, user):
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/auth/profile/')

    assert response.status_code == 200
    assert response.data['username'] == 'testuser'

@pytest.mark.django_db
def test_profile_requires_authentication(api_client):
    response = api_client.get('/api/auth/profile/')

    assert response.status_code == 401