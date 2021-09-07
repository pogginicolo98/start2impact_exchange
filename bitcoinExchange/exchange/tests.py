import json
from django.contrib.auth.models import User
from django.urls import reverse
from exchange.api.serializers import OrderSerializer, ProfileSerializer
from exchange.models import Order
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class RESTAuthTestCase(APITestCase):
    """
    Django REST Auth configuration test case.

    :tests
    - test_authentication(): Log in with a user via Django REST Auth APIs.
    - test_registration(): Register a new user via Django REST Auth APIs.
    """

    test_url = reverse('profile-detail')

    def setUp(self):
        self.user = User.objects.create_user(username='testcase1', password='Change_me_123!')

    def test_authentication(self):
        credentials = {
            'username': 'testcase1',
            'password': 'Change_me_123!'
        }
        response = self.client.post('http://127.0.0.1:8000/api/rest-auth/login/', data=credentials)
        json_response = json.loads(response.content)
        token = f"Token {json_response['key']}"
        headers = {'Authorization': token}
        response = self.client.get(self.test_url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_registration(self):
        data = {
            'username': 'testcase2',
            'email': 'testcase@local.app',
            'password1': 'Change_me_123!',
            'password2': 'Change_me_123!',
        }
        response = self.client.post('/api/rest-auth/registration/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class OrderViewSetTestCase(APITestCase):
    """
    OrderViewSet test case.

    :actions
    - list
    - create
    - retrieve
    - delete
    """

    def setUp(self):
        """
        Create new user, get an authentication token and authenticate with it.
        Create an order for tests and setup urls.
        """
        self.user = User.objects.create_user(username='testcase', password='Change_me_123!')
        self.order = Order.objects.create(profile=self.user.profile, price=5.5, quantity=0.5, type='S')
        self.list_url = reverse('orders-list')
        self.detail_url = reverse('orders-detail', kwargs={'pk': self.order.pk})
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_list_order_by_not_authenticated_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)  # Ex. URL: http://127.0.0.1/api/orders/
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_order_by_authenticated_user(self):
        response = self.client.get(self.list_url)  # Ex. URL: http://127.0.0.1/api/orders/
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order_by_not_authenticated_user(self):
        data = {'price': 10.5, 'quantity': 0.5, 'type': 'S'}
        self.client.force_authenticate(user=None)
        response = self.client.post(self.list_url, data=data)  # Ex. URL: http://127.0.0.1/api/orders/
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_by_authenticated_user(self):
        data = {'price': 20.5, 'quantity': 0.5, 'type': 'S'}
        response = self.client.post(self.list_url, data=data)  # Ex. URL: http://127.0.0.1/api/orders/
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json_response = json.loads(response.content)
        self.assertEqual(response.data['profile'], 'testcase')  # Checking the data that the response was created with
        self.assertEqual(json_response['price'], 20.5)  # Checking the fully rendered response

    def test_create_order_invalid(self):
        data = {'price': 10.5, 'quantity': 11, 'type': 'S'}
        response = self.client.post(self.list_url, data=data)  # Ex. URL: http://127.0.0.1/api/orders/
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['non_field_errors'], ['insufficient balance'])  # Checking the fully rendered response

    def test_retrieve_order_by_not_authenticated_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.detail_url)  # Ex. URL: http://127.0.0.1/api/orders/1/
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_order_by_random_user(self):
        random_user = User.objects.create_user(username='hacker', password='Change_me_123!')
        self.client.force_authenticate(user=random_user)
        response = self.client.get(self.detail_url)  # Ex. URL: http://127.0.0.1/api/orders/1/
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_order_by_authenticated_user(self):
        serializer_data = OrderSerializer(instance=self.order).data
        response = self.client.get(self.detail_url)  # Ex. URL: http://127.0.0.1/api/orders/1/
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(response.content)
        self.assertEqual(json_response, serializer_data)  # Checking the fully rendered response

    def test_delete_order_by_not_authenticated_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.detail_url)  # Ex. URL: http://127.0.0.1/api/orders/1/
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order_by_random_user(self):
        random_user = User.objects.create_user(username='hacker', password='Change_me_123!')
        self.client.force_authenticate(user=random_user)
        response = self.client.delete(self.detail_url)  # Ex. URL: http://127.0.0.1/api/orders/1/
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_by_authenticated_user(self):
        response = self.client.delete(self.detail_url)  # Ex. URL: http://127.0.0.1/api/orders/1/
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(self.detail_url)  # Ex. URL: http://127.0.0.1/api/orders/1/
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LatestOrdersListAPIViewTestCase(APITestCase):
    """
    LatestOrdersListAPIView test case.

    :actions
    - list
    """

    def setUp(self):
        """
        Create new user, get an authentication token and authenticate with it.
        Create an order for tests and setup url.
        """
        self.user = User.objects.create_user(username='testcase1', password='Change_me_123!')
        self.order = Order.objects.create(profile=self.user.profile, price=5.5, quantity=0.5, type='S')
        self.list_url = reverse('orders-latest')
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_list_latest_orders_by_not_authenticated_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)  # Ex. URL: http://127.0.0.1/api/orders/latest/
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_latest_orders_by_authenticated_user(self):
        user = User.objects.create_user(username='testcase2', password='Change_me_123!')
        Order.objects.create(profile=user.profile, price=10.5, quantity=0.5, type='S')
        response = self.client.get(self.list_url)  # Ex. URL: http://127.0.0.1/api/orders/latest/
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(response.content)
        self.assertEqual(json_response[0]['id'], 2)  # Checking the fully rendered response
        self.assertEqual(json_response[0]['price'], 10.5)  # Checking the fully rendered response


class ProfileAPIViewTestCase(APITestCase):
    """
    ProfileAPIView test case.

    :actions
    - retrieve
    """

    def setUp(self):
        """
        Create new user, get an authentication token and authenticate with it.
        """
        self.user = User.objects.create_user(username='testcase1', password='Change_me_123!')
        self.list_url = reverse('profile-detail')
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_retrieve_profile_by_not_authenticated_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)  # Ex. URL: http://127.0.0.1/api/profile/
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_profile_by_authenticated_user(self):
        serializer_data = ProfileSerializer(instance=self.user.profile).data
        response = self.client.get(self.list_url)  # Ex. URL: http://127.0.0.1/api/profile/
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(response.content)
        self.assertEqual(json_response, serializer_data)  # Checking the fully rendered response
