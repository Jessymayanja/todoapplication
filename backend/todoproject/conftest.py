import pytest
from rest_framework.test import APIClient
from mytodoapp.models import CustomUser, Todo
from django.utils import timezone
from datetime import timedelta


@pytest.fixture
def api_client():
    """A bare apt client - not authenticated."""
    return APIClient()


@pytest.fixture
def verified_user():
    """A fully verified user ready to log in."""
    user = CustomUser.objects.create(
        username='testuser',
        email='testuser@example.com',
        password='StrongPass231',
    )
    user.is_verified = True
    user.save()
    return user


@pytest.fixture
def auth_client(api_client, verified_user):
    """An authenticated client for a verified user."""
    response = api_client.post('/api/token/', {
        'username': 'testuser',
        'password': 'StrongPass231',
    }, format='json')
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def sample_todo(verified_user):
    """A sample incomplete todo belonging to verified_user."""
    return Todo.objects.create(
        user=verified_user,
        description='Buy groceries',
        deadline=timezone.now() + timedelta(days=2),
        completion=False,
    )

