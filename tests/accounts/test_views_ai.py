import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.django_db
class TestAIChatView:
    url = "/api/ai/chat/"

    @patch("accounts.views.OpenAI")
    def test_ai_chat_success(self, MockOpenAI, auth_client):
        client, user = auth_client
        
        # Mocking the OpenAI client response
        mock_instance = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello, I am AI!"))]
        mock_instance.chat.completions.create.return_value = mock_response

        response = client.post(self.url, {"message": "Hello"})
        assert response.status_code == 200
        assert response.data["reply"] == "Hello, I am AI!"
        
        # Verify OpenAI was called correctly
        mock_instance.chat.completions.create.assert_called_once()
        args, kwargs = mock_instance.chat.completions.create.call_args
        assert kwargs["model"] == "gpt-3.5-turbo"
        assert len(kwargs["messages"]) == 2
        assert kwargs["messages"][1]["content"] == "Hello"

    def test_ai_chat_missing_message(self, auth_client):
        client, user = auth_client
        response = client.post(self.url, {})
        assert response.status_code == 400
        assert "error" in response.data

    @patch("accounts.views.OpenAI")
    def test_ai_chat_api_failure(self, MockOpenAI, auth_client):
        client, user = auth_client
        
        mock_instance = MockOpenAI.return_value
        mock_instance.chat.completions.create.side_effect = Exception("API rate limit exceeded")

        response = client.post(self.url, {"message": "Hello"})
        assert response.status_code == 500
        assert "API rate limit exceeded" in response.data["error"]

    def test_ai_chat_unauthenticated(self, api_client):
        response = api_client.post(self.url, {"message": "Hello"})
        assert response.status_code == 401
