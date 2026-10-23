import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from api.models import Category, Product

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        username = 'testuser',
        email = 'test@example.com',
        password = 'TestPassword123'
    )

@pytest.fixture
def admin_user():
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='AdminPassword123',
        is_staff = True,
        is_superuser = True
    )

@pytest.fixture
def category():
    return Category.objects.create(
        name='Electronics',
        description='Electronics Products'
    )

@pytest.fixture
def product(category):
    return Product.objects.create(
        name = 'Samsung Galaxy S25',
        description = 'Samsung smartphone',
        price = 50000,
        stock = 10,
        category = category,
        is_active = True
    )