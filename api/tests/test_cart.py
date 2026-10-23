import pytest

@pytest.mark.django_db
def test_get_cart(api_client, user):
    api_client.force_authenticate(user = user)
    response = api_client.get('/api/cart')
    assert response.status_code == 200
    assert 'items' in response.data

@pytest.mark.django_db
def test_add_product_to_cart(api_client, user, product):
    api_client.force_authenticate(user= user)
    response = api_client.post(
        '/api/cart/items/',
        {
            'product': product.id,
            'quantity': 2
        },
        format = 'json'

    )
    assert response.status_code in [200, 201]

@pytest.mark.django_db
def test_crat_rejects_qunatity_above_stock(api_client, user, product):
    api_client.force_authenticate(user= user)
    response = api_client.post(
        '/api/cart/items/',
        {
            'product': product.id,
            'quantity': 100
        },
        format= 'json'
    )
    assert response.status_code == 400