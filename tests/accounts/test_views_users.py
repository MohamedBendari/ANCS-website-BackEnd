import pytest
from django.contrib.auth.models import User
from accounts.models import Profile

@pytest.mark.django_db
class TestUserManagementViews:
    
    def test_list_users_admin(self, admin_client, user_factory):
        client, admin = admin_client
        user_factory.create_batch(3)
        response = client.get("/api/users/")
        assert response.status_code == 200
        # 3 users + 1 admin = 4
        assert len(response.data) == 4

    def test_list_users_normal_user(self, auth_client):
        client, user = auth_client
        response = client.get("/api/users/")
        assert response.status_code == 403

    def test_delete_user_admin(self, admin_client, user_factory):
        client, admin = admin_client
        user = user_factory()
        response = client.delete(f"/api/users/{user.id}/delete/")
        assert response.status_code == 200
        assert not User.objects.filter(id=user.id).exists()

    def test_delete_user_not_found(self, admin_client):
        client, admin = admin_client
        response = client.delete("/api/users/9999/delete/")
        assert response.status_code == 404

    def test_update_user_admin(self, admin_client, user_factory):
        client, admin = admin_client
        user = user_factory(username="oldname")
        data = {
            "username": "newname",
            "role": "admin",
            "is_active": False
        }
        response = client.put(f"/api/users/{user.id}/update/", data)
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.username == "newname"
        assert not user.is_active
        assert user.is_staff
        assert user.is_superuser
        assert Profile.objects.get(user=user).role == "admin"

    def test_update_user_not_found(self, admin_client):
        client, admin = admin_client
        response = client.put("/api/users/9999/update/", {})
        assert response.status_code == 404
