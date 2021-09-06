import json
from django.contrib.auth.models import User
from django.urls import reverse
from exchange.api.serializers import OrderSerializer
from exchange.models import Order, Profile, Transaction, Wallet
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
    - create
    - retrieve
    - list
    - delete

    :tests
    - test_profile_list_not_authenticated(): Test 'list()' action by an unauthenticated user.
    - test_profile_list_authenticated(): Test 'list()' action by an authenticated user.
    - test_profile_retrieve_not_authenticated(): Test 'retrieve()' action by an unauthenticated user.
    - test_profile_retrieve_authenticated(): Test 'retrieve()' action by an authenticated user.
    - test_profile_update_by_not_authenticated_user(): Test 'update()' action by an unauthenticated user.
    - test_profile_update_by_random_user(): Test 'update()' action by a random authenticated user.
    - test_profile_update_by_owner(): Test 'update()' action by the user who created the 'Profile' instance.
    """

    list_url = reverse('orders-list')
    detail_url = reverse('orders-detail', kwargs={'pk': 1})

    def setUp(self):
        """
        Create new user, get an authentication token and authenticate with it.
        """
        self.user = User.objects.create_user(username='testcase', password='Change_me_123!')
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()
        self.order = Order.objects.create(profile=self.user.profile, price=10, quantity=1, type='S')

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_retrieve_orders_not_authenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.detail_url)  # Ex. URL: http://127.0.0.1/api/orders/1/
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_order_authenticated(self):
        serializer_data = OrderSerializer(instance=self.order).data
        print(serializer_data)
        # response = self.client.get(self.detail_url)  # Ex. URL: http://127.0.0.1/api/orders/1/
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # json_response = json.loads(response.content)
        # self.assertEqual(json_response, 'serializer_data')  # Checking the fully rendered response

    def test_create_order_not_authenticated(self):
        data = {'price': 10.5, 'quantity': 1.0, 'type': 'S'}
        self.client.force_authenticate(user=None)
        response = self.client.post(self.list_url, data=data)  # Ex. URL: http://127.0.0.1/api/orders/
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_authenticated(self):
        data = {'price': 10.5, 'quantity': 1.0, 'type': 'S'}
        response = self.client.post(self.list_url, data=data)  # Ex. URL: http://127.0.0.1/api/orders/
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json_response = json.loads(response.content)
        self.assertEqual(response.data['profile'], 'testcase')  # Checking the data that the response was created with
        self.assertEqual(json_response['price'], 10.5)  # Checking the fully rendered response

    def test_create_order_invalid(self):
        data = {'price': 10.5, 'quantity': 11, 'type': 'S'}
        response = self.client.post(self.list_url, data=data)  # Ex. URL: http://127.0.0.1/api/orders/
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['non_field_errors'], ['insufficient balance'])  # Checking the fully rendered response

    #
    # def test_profile_update_by_not_authenticated_user(self):
    #     data = {
    #         'bio': 'Hacked!',
    #         'city': 'hackland'
    #     }
    #     self.client.force_authenticate(user=None)
    #     response = self.client.put(self.detail_url, data=data)  # Ex. URL: http://127.0.0.1/api/profiles/1/
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    # def test_profile_update_by_random_user(self):
    #     data = {
    #         'bio': 'Hacked!',
    #         'city': 'hackland'
    #     }
    #     random_user = User.objects.create_user(username='hacker', password='Change_me_123!')  # pk: 2
    #     self.client.force_authenticate(user=random_user)
    #     response = self.client.put(self.detail_url, data=data)  # Ex. URL: http://127.0.0.1/api/profiles/1/
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    # def test_profile_update_by_owner(self):
    #     data = {
    #         'bio': 'Test bio',
    #         'city': 'testland'
    #     }
    #     expected_data = {
    #         "id": 1,
    #         "user": "testcase",
    #         "avatar": None,
    #         "bio": "Test bio",
    #         "city": "testland"
    #     }
    #     response = self.client.put(self.detail_url, data=data)  # Ex. URL: http://127.0.0.1/api/profiles/1/
    #     json_response = json.loads(response.content)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(json_response, expected_data)  # Checking the fully rendered response
