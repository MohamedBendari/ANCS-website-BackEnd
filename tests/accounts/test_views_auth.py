import pytest
from django.contrib.auth.models import User
from accounts.models import Profile

@pytest.mark.django_db
class TestRegisterView:
    url = "/api/register/"

    def test_register_success(self, api_client):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "strongpassword123"
        }
        response = api_client.post(self.url, data)
        assert response.status_code == 201
        assert User.objects.filter(username="newuser").exists()

    def test_register_missing_data(self, api_client):
        response = api_client.post(self.url, {})
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginView:
    url = "/api/login/"

    def test_login_success(self, api_client, user_factory):
        user = user_factory(username="testlogin", password="mypassword")
        data = {"username": "testlogin", "password": "mypassword"}
        response = api_client.post(self.url, data)
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["role"] == "user"

    def test_login_invalid_credentials(self, api_client, user_factory):
        user = user_factory(username="testlogin", password="mypassword")
        data = {"username": "testlogin", "password": "wrongpassword"}
        response = api_client.post(self.url, data)
        assert response.status_code == 400
        assert "error" in response.data

    def test_login_missing_fields(self, api_client):
        response = api_client.post(self.url, {"username": "test"})
        assert response.status_code == 400


@pytest.mark.django_db
class TestAdminLoginView:
    url = "/api/admin/login/"

    def test_admin_login_success(self, api_client, admin_user_factory):
        admin = admin_user_factory(username="adminuser", password="mypassword")
        # Ensure role is admin
        profile = Profile.objects.get(user=admin)
        profile.role = 'admin'
        profile.save()

        data = {"username": "adminuser", "password": "mypassword"}
        response = api_client.post(self.url, data)
        assert response.status_code == 200
        assert "access" in response.data
        assert response.data["role"] == "admin"

    def test_admin_login_forbidden_for_normal_user(self, api_client, user_factory):
        user = user_factory(username="normaluser", password="mypassword")
        data = {"username": "normaluser", "password": "mypassword"}
        response = api_client.post(self.url, data)
        assert response.status_code == 403
        assert "error" in response.data

@pytest.mark.django_db
class TestChangePasswordView:
    url = "/api/change-password/"

    def test_change_password_success(self, auth_client):
        client, user = auth_client
        user.set_password("oldpassword")
        user.save()

        data = {
            "old_password": "oldpassword",
            "new_password": "newpassword123"
        }
        response = client.post(self.url, data)
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password("newpassword123")

    def test_change_password_wrong_old(self, auth_client):
        client, user = auth_client
        user.set_password("oldpassword")
        user.save()

        data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        response = client.post(self.url, data)
        assert response.status_code == 400

    def test_change_password_too_short(self, auth_client):
        client, user = auth_client
        user.set_password("oldpassword")
        user.save()

        data = {
            "old_password": "oldpassword",
            "new_password": "123"
        }
        response = client.post(self.url, data)
        assert response.status_code == 400

    def test_change_password_unauthenticated(self, api_client):
        response = api_client.post(self.url, {})
        assert response.status_code == 401
