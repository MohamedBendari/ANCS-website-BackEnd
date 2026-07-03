import pytest
from django.contrib.auth.models import User
from accounts.models import Profile

@pytest.mark.django_db
class TestProfileModel:

    def test_profile_creation(self, user_factory):
        user = user_factory()
        # Profile is created automatically by signal, so we just get it
        profile = Profile.objects.get(user=user)
        assert profile.user == user
        assert profile.role == 'user'

    def test_profile_str_method(self, user_factory):
        user = user_factory(username="johndoe")
        profile = Profile.objects.get(user=user)
        assert str(profile) == "johndoe"
