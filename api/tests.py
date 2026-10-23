from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Order


class PublicApiTests(APITestCase):
	def test_home_returns_api_status(self):
		response = self.client.get('/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['status'], 'success')

	def test_register_creates_user(self):
		response = self.client.post('/api/auth/register/', {
			'username': 'new-user',
			'email': 'new@example.com',
			'password': 'strong-password-123',
		}, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(User.objects.filter(username='new-user').exists())

	def test_register_rejects_short_password(self):
		response = self.client.post('/api/auth/register/', {
			'username': 'new-user',
			'email': 'new@example.com',
			'password': 'short',
		}, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertFalse(User.objects.filter(username='new-user').exists())


class AdminApiTests(APITestCase):
	def test_admin_endpoint_requires_staff_user(self):
		response = self.client.get('/api/admin/test/')

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_admin_endpoint_allows_staff_user(self):
		user = User.objects.create_user(
			username='admin-user',
			password='strong-password-123',
			is_staff=True,
		)
		self.client.force_authenticate(user=user)

		response = self.client.get('/api/admin/test/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['message'], 'Welcome Admin!')


class OrderApiTests(APITestCase):
	def test_update_order_status_updates_value_for_authenticated_user(self):
		user = User.objects.create_user(
			username='buyer-user',
			password='strong-password-123',
		)
		order = Order.objects.create(user=user, status=Order.OrderStatus.PENDING)
		self.client.force_authenticate(user=user)

		response = self.client.patch(
			f'/api/orders/{order.id}/status/',
			{'status': Order.OrderStatus.SHIPPED},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['status'], Order.OrderStatus.SHIPPED)
		order.refresh_from_db()
		self.assertEqual(order.status, Order.OrderStatus.SHIPPED)
