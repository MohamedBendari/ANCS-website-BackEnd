import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from accounts.models import Profile

@pytest.mark.django_db
class TestGoogleLoginView:
    url = "/api/auth/google/"

    @patch("urllib.request.urlopen")
    def test_google_login_access_token_success(self, mock_urlopen, api_client):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"email": "google@example.com", "name": "Google User"}'
        
        # Enter the context manager for urlopen
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        response = api_client.post(self.url, {"access_token": "valid_token"})
        
        assert response.status_code == 200
        assert response.data["email"] == "google@example.com"
        assert response.data["name"] == "Google User"
        assert "access" in response.data
        
        user = User.objects.get(email="google@example.com")
        assert user.first_name == "Google User"
        assert Profile.objects.filter(user=user).exists()

    @patch("accounts.views.id_token.verify_oauth2_token")
    def test_google_login_id_token_success(self, mock_verify, api_client):
        mock_verify.return_value = {"email": "idtoken@example.com", "name": "ID Token User"}
        
        response = api_client.post(self.url, {"token": "valid_id_token"})
        
        assert response.status_code == 200
        assert response.data["email"] == "idtoken@example.com"
        assert "access" in response.data

    def test_google_login_missing_token(self, api_client):
        response = api_client.post(self.url, {})
        assert response.status_code == 400
        assert "Token is required" in response.data["error"]

    @patch("accounts.views.id_token.verify_oauth2_token")
    def test_google_login_invalid_token(self, mock_verify, api_client):
        mock_verify.side_effect = ValueError("Wrong token")
        
        response = api_client.post(self.url, {"token": "invalid"})
        assert response.status_code == 400
        assert "Wrong token" in response.data["error"]
