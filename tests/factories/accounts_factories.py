import factory
from django.contrib.auth.models import User
from accounts.models import Profile

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or "password123"
        self.set_password(password)

class AdminUserFactory(UserFactory):
    is_staff = True
    is_superuser = True
    username = factory.Sequence(lambda n: f"admin_{n}")
    email = factory.Sequence(lambda n: f"admin_{n}@example.com")

class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    # Using factory.SubFactory(UserFactory) will create a User, which in turn triggers the post_save signal and creates a Profile.
    # To avoid UniqueConstraint failure, we must use django_get_or_create or simply fetch the auto-created profile.
    # A common pattern is to just let the signal create it, and if we need a specific Profile, we fetch it.
    pass

def get_or_create_profile(user, role='user'):
    profile, created = Profile.objects.get_or_create(user=user)
    profile.role = role
    profile.save()
    return profile
