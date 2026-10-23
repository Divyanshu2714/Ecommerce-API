from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductViewSet, admin_test, home, profile, register, my_cart, add_to_cart, update_cart_item, remove_cart_item, create_order, my_orders, order_details, update_order_status

router = DefaultRouter()

router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', home, name='home'),
    path('auth/register/', register, name='register'),
    path('auth/profile/', profile, name='profile'),
    path('admin/test/', admin_test, name='admin_test'),
    path('cart', my_cart, name='my-cart-no-slash'),
    path('cart/', my_cart, name='my-cart'),
    path('cart/items', add_to_cart, name='add-to-cart-no-slash'),
    path('cart/items/', add_to_cart, name='add-to-cart'),
    path('cart/items/<int:item_id>', update_cart_item, name='update-cart-item-no-slash'),
    path('cart/items/<int:item_id>/', update_cart_item, name='update-cart-item'),
    path('cart/items/<int:item_id>/remove', remove_cart_item, name='remove-cart-item-no-slash'),
    path('cart/items/<int:item_id>/remove/', remove_cart_item, name='remove-cart-item'),
    path('products', ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list-no-slash'),
    path('products/', ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    path('products/<int:pk>', ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='product-detail-no-slash'),
    path('products/<int:pk>/', ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='product-detail'),
    path('orders', my_orders, name='my-orders-no-slash'),
    path('orders/', my_orders, name='my-orders'),
    path('orders/create', create_order, name='create-order-no-slash'),
    path('orders/create/', create_order, name='create-order'),
    path('orders/<int:order_id>', order_details, name='order-details-no-slash'),
    path('orders/<int:order_id>/', order_details, name='order-details'),
    path('orders/<int:order_id>/status', update_order_status, name='update-order-status-no-slash'),
    path('orders/<int:order_id>/status/', update_order_status, name='update-order-status'),
    path('', include(router.urls)),
]