import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client(api_client, user_factory):
    user = user_factory()
    api_client.force_authenticate(user=user)
    return api_client, user

@pytest.fixture
def admin_client(api_client, admin_user_factory):
    admin = admin_user_factory()
    api_client.force_authenticate(user=admin)
    return api_client, admin
