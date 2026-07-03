import pytest
from django.urls import reverse
from contact.models import ContactMessage

# Since urls are not registered in the app explicitly, they might be in backend.urls.
# But let's assume standard DRF endpoints based on views.
# We will use hardcoded paths if reverse names are not defined.
# Let's inspect backend/urls.py if we have to, but since we know the views: ContactMessageListView, DeleteMessageView.
# I will just use standard mock URLs for tests to ensure the view logic is tested directly via RequestFactory or APIClient.

@pytest.mark.django_db
class TestContactMessageListView:
    url = "/api/messages/"  # Updated to match actual url

    def test_list_messages_unauthenticated(self, api_client, contact_message_factory):
        contact_message_factory.create_batch(3)
        # Any user can post, but only authenticated (admin?) can read based on permissions.
        # Wait, the view says IsAuthenticated for read, POST for anyone.
        # "القراءة للـ admin بس" -> IsAuthenticated() in get_permissions.
        response = api_client.get(self.url)
        assert response.status_code == 401

    def test_list_messages_authenticated(self, auth_client, contact_message_factory):
        client, user = auth_client
        contact_message_factory.create_batch(3)
        response = client.get(self.url)
        # Auth client should be able to get if they are authenticated.
        assert response.status_code == 200
        assert len(response.data) == 3

    def test_create_message_unauthenticated(self, api_client):
        data = {
            "name": "New User",
            "email": "new@example.com",
            "purpose": "buy",
            "message": "I want to buy"
        }
        response = api_client.post(self.url, data)
        assert response.status_code == 201
        assert ContactMessage.objects.count() == 1
        assert ContactMessage.objects.first().name == "New User"

    def test_search_messages(self, auth_client, contact_message_factory):
        client, user = auth_client
        contact_message_factory(name="Unique Name Search")
        contact_message_factory(name="Other")
        
        response = client.get(f"{self.url}?search=Unique")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Unique Name Search"


@pytest.mark.django_db
class TestDeleteMessageView:
    
    def get_url(self, message_id):
        return f"/api/messages/{message_id}/delete/"

    def test_delete_message_admin(self, admin_client, contact_message_factory):
        client, admin = admin_client
        message = contact_message_factory()
        response = client.delete(self.get_url(message.id))
        assert response.status_code == 200
        assert ContactMessage.objects.count() == 0

    def test_delete_message_normal_user(self, auth_client, contact_message_factory):
        client, user = auth_client
        message = contact_message_factory()
        response = client.delete(self.get_url(message.id))
        # Normal user should be 403 Forbidden because IsAdminUser permission
        assert response.status_code == 403
        assert ContactMessage.objects.count() == 1

    def test_delete_nonexistent_message(self, admin_client):
        client, admin = admin_client
        response = client.delete(self.get_url(9999))
        assert response.status_code == 404
