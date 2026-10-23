import pytest
from api.models import Order, OrderItem

@pytest.mark.django_db
def test_create_order_from_cart(api_client,user, product):
    api_client.force_authenticate(user=user)
    cart_response = api_client.post(
        '/api/cart/items/',
        {
            'product': product.id,
            'quantity': 2
        },
        format = 'json'
    )
    assert cart_response.status_code in [200, 201]
    response = api_client.post(
        '/api/orders/create/',
        format = 'json'
    )
    assert response.status_code == 201
    assert Order.objects.filter(
        user=user
    ).exists()

@pytest.mark.django_db
def test_checkout_reduces_stock(api_client,user,product):
    api_client.force_authenticate(user=user)
    initial_stock = product.stock
    api_client.post(
        '/api/cart/items/',
        {
            'product': product.id,
            'quantity': 2
        },
        format = 'json'
    )
    response = api_client.post(
        '/api/orders/create/',
        format='json'
    )
    assert response.status_code == 201
    product.refresh_from_db()
    assert product.stock == initial_stock - 2

@pytest.mark.django_db
def test_order_item_stores_product_price(api_client, user, product):
    api_client.force_authenticate(user=user)
    original_price = product.price
    api_client.post(
        '/api/cart/items/',
        {
            'product': product.id,
            'quantity': 2
        },
        format = 'json'
    )
    response = api_client.post(
        '/api/orders/create/',
        format = 'json'
    )
    assert response.status_code == 201
    order = Order.objects.get(user=user)
    item = OrderItem.objects.get(order = order)
    assert item.price == original_price
    assert item.quantity == 2