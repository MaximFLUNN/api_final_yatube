import pytest


@pytest.fixture
def password():
    return 'secure_password_123'


@pytest.fixture
def user(django_user_model, password):
    return django_user_model.objects.create_user(
        username='MainTestAccount',
        password=password
    )


@pytest.fixture
def another_user(django_user_model, password):
    return django_user_model.objects.create_user(
        username='SecondaryTestAccount',
        password=password
    )


@pytest.fixture
def token(user):
    from rest_framework.authtoken.models import Token
    token_obj, created = Token.objects.get_or_create(user=user)
    return token_obj.key


@pytest.fixture
def user_client(token):
    from rest_framework.test import APIClient
    
    api_client = APIClient()
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return api_client
