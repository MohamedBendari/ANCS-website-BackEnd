import pytest
from contact.serializers import ContactMessageSerializer
from contact.models import ContactMessage

@pytest.mark.django_db
class TestContactMessageSerializer:
    
    def test_serializer_valid_data(self):
        data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "purpose": "question",
            "message": "I have a question."
        }
        serializer = ContactMessageSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.name == "Jane Doe"

    def test_serializer_missing_required_fields(self):
        data = {
            "name": "Jane Doe",
        }
        serializer = ContactMessageSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors
        assert "purpose" in serializer.errors
        assert "message" in serializer.errors

    def test_serializer_invalid_email(self):
        data = {
            "name": "Jane Doe",
            "email": "not-an-email",
            "purpose": "question",
            "message": "I have a question."
        }
        serializer = ContactMessageSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_serializer_invalid_purpose(self):
        data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "purpose": "invalid_purpose",
            "message": "I have a question."
        }
        serializer = ContactMessageSerializer(data=data)
        assert not serializer.is_valid()
        assert "purpose" in serializer.errors

    def test_serializer_output_data(self, contact_message_factory):
        message = contact_message_factory()
        serializer = ContactMessageSerializer(message)
        data = serializer.data
        assert data["name"] == message.name
        assert data["email"] == message.email
        assert data["purpose"] == message.purpose
        assert data["message"] == message.message
        assert "created_at" in data
        assert "is_read" in data
