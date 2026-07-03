import pytest
from accounts.serializers import RegisterSerializer, UserManagementSerializer
from django.contrib.auth.models import User
from accounts.models import Profile
from tests.factories.accounts_factories import get_or_create_profile

@pytest.mark.django_db
class TestRegisterSerializer:

    def test_valid_data(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "strongpassword"
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.username == "newuser"
        assert user.check_password("strongpassword")

    def test_missing_password(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_missing_username(self):
        data = {
            "password": "strongpassword",
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "username" in serializer.errors

    def test_fallback_username(self):
        data = {
            "email": "fallback@example.com",
            "password": "strongpassword"
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.username == "fallback"

    def test_fallback_username_other_fields(self):
        data = {
            "firstName": "John",
            "password": "strongpassword"
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["username"] == "John"


@pytest.mark.django_db
class TestUserManagementSerializer:

    def test_serializer_output(self, user_factory):
        user = user_factory(username="mgmtuser", email="mgmt@example.com", is_active=True)
        profile = get_or_create_profile(user, role="admin")
        
        serializer = UserManagementSerializer(user)
        assert serializer.data["username"] == "mgmtuser"
        assert serializer.data["email"] == "mgmt@example.com"
        assert serializer.data["role"] == "admin"
        assert serializer.data["is_active"] is True
        assert "date_joined" in serializer.data
