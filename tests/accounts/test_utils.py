import pytest
from accounts.views import get_login_fields, authenticate_user
from django.contrib.auth.models import User

class MockRequest:
    def __init__(self, data):
        self.data = data

@pytest.mark.django_db
class TestAccountsUtils:

    def test_get_login_fields(self):
        # test username
        req = MockRequest({"username": "testuser", "password": "123"})
        ident, pwd = get_login_fields(req)
        assert ident == "testuser"
        assert pwd == "123"

        # test email fallback
        req = MockRequest({"email": "test@example.com", "pass": "123"})
        ident, pwd = get_login_fields(req)
        assert ident == "test@example.com"
        assert pwd == "123"

        # test empty
        req = MockRequest({})
        ident, pwd = get_login_fields(req)
        assert ident is None
        assert pwd is None

        # test dict fallback
        req = MockRequest({"random_key": "some_value", "password1": "abc"})
        ident, pwd = get_login_fields(req)
        assert ident == "some_value"
        assert pwd == "abc"

    def test_authenticate_user_username(self, user_factory):
        user = user_factory(username="auth_test", password="mypassword")
        auth_user = authenticate_user("auth_test", "mypassword")
        assert auth_user == user

    def test_authenticate_user_email(self, user_factory):
        user = user_factory(username="auth_test2", email="auth@example.com", password="mypassword")
        auth_user = authenticate_user("auth@example.com", "mypassword")
        assert auth_user == user

    def test_authenticate_user_invalid(self, user_factory):
        user_factory(username="auth_test", password="mypassword")
        auth_user = authenticate_user("auth_test", "wrongpassword")
        assert auth_user is None
        
        auth_user = authenticate_user("nonexistent", "mypassword")
        assert auth_user is None
        
        auth_user = authenticate_user(None, None)
        assert auth_user is None
        
        auth_user = authenticate_user("auth@example.com", "wrong")
        assert auth_user is None
