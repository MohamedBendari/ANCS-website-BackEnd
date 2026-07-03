import pytest
from django.contrib.auth.models import User
from accounts.models import Profile

@pytest.mark.django_db
class TestProfileSignals:

    def test_create_profile_signal(self):
        user = User.objects.create(username="signal_test", password="123")
        assert Profile.objects.filter(user=user).exists()
        
    def test_create_profile_signal_not_duplicate(self):
        user = User.objects.create(username="signal_test2", password="123")
        # Save again to trigger signal with created=False
        user.save()
        assert Profile.objects.filter(user=user).count() == 1
