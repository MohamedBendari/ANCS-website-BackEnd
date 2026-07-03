from pytest_factoryboy import register
from .accounts_factories import UserFactory, AdminUserFactory
from .contact_factories import ContactMessageFactory

register(UserFactory)
register(AdminUserFactory)
register(ContactMessageFactory)
