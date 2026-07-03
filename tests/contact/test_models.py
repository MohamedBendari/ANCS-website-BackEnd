import pytest
from contact.models import ContactMessage
from tests.factories.contact_factories import ContactMessageFactory

@pytest.mark.django_db
class TestContactMessageModel:
    
    def test_contact_message_creation(self):
        message = ContactMessageFactory(name="Test User", purpose="support")
        assert message.id is not None
        assert message.name == "Test User"
        assert message.purpose == "support"
        assert not message.is_read
        assert message.created_at is not None

    def test_contact_message_str_method(self):
        message = ContactMessageFactory(name="John Doe")
        assert str(message) == "John Doe"

    def test_default_values(self):
        message = ContactMessage.objects.create(
            name="Alice",
            email="alice@example.com",
            purpose="buy",
            message="Hello"
        )
        assert message.is_read is False

    @pytest.mark.parametrize("purpose", ['buy', 'support', 'question', 'partnership'])
    def test_valid_purposes(self, purpose):
        message = ContactMessageFactory(purpose=purpose)
        assert message.purpose == purpose
