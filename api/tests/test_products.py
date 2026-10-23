import pytest

@pytest.mark.django_db
def test_product_list(api_client, user , product):
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/products')
    assert response.status_code == 200

@pytest.mark.django_db
def test_product_search(api_client, user, product):
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/products/?search=Samsung')
    assert response.status_code == 200

@pytest.mark.django_db
def test_normal_user_cannot_create(api_client, user, category):
    api_client.force_authenticate(user=user)
    response = api_client.post(
        '/api/products/',
        {
            'name': 'iPhone 17',
            'description': 'Apple smartphone',
            'price': 70000,
            'stock': 10,
            'category': category.id,
            'is_active': True
        },
        format = 'json'
    )

    assert response.status_code == 403

@pytest.mark.django_db
def test_admin_can_create_product(api_client, admin_user, category):
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(
        '/api/products',
        {
            'name': 'iPhone 17',
            'description': 'Apple smartphone',
            'price': 70000,
            'stock': 10,
            'category': category.id,
            'is_active': True
        },
        format = 'json'
    )
    assert response.status_code == 201

@pytest.mark.django_db
def test_product_rejects_negative_price(api_client, admin_user, category):
    api_client.force_authenticate(user = admin_user)
    response = api_client.post(
        '/api/products/',
        {
            'name': 'Invalid Product',
            'description': 'Invalid Product',
            'price': -100,
            'stock': 10,
            'category': category.id,
            'is_active': True
        },
        format = 'json'
    )
    assert response.status_code == 400

@pytest.mark.django_db
def test_product_rejects_negative_stock(api_client, admin_user, category):
    api_client.force_authenticate(user = admin_user)
    response = api_client.post(
        '/api/products/',
        {
            'name': 'Invalid Product',
            'description': 'Invalid Product',
            'price': 1000,
            'stock': -5,
            'category': category.id,
            'is_active': True
        },
        format = 'json'
    )
    assert response.status_code == 400