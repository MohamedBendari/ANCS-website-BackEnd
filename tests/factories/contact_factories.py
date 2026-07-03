import factory
from contact.models import ContactMessage

class ContactMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactMessage

    name = factory.Faker("name")
    email = factory.Faker("email")
    purpose = factory.Iterator(['buy', 'support', 'question', 'partnership'])
    message = factory.Faker("text")
    is_read = False
