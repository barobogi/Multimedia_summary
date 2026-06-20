"""Shared fixtures for all tests"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def mock_settings():
    """Patch settings so tests don't need real API keys."""
    with patch("app.config.Settings", autospec=True) as MockSettings:
        instance = MockSettings.return_value
        instance.anthropic_api_key = "test-key"
        instance.github_token = "test-token"
        instance.gmail_user = "test@example.com"
        instance.gmail_refresh_token = None
        instance.gmail_client_id = None
        instance.gmail_client_secret = None
        instance.github_repo = "barobogi/Daily_for_Barobogi"
        instance.github_username = "barobogi"
        instance.drive_type = "onedrive"
        instance.drive_folder_id = None
        instance.drive_refresh_token = None
        instance.debug = False
        instance.port = 8000
        instance.workers = 1
        instance.log_level = "WARNING"
        instance.claude_model = "claude-3-5-sonnet-20241022"
        instance.max_tokens_summary = 2000
        instance.max_tokens_analysis = 1000
        yield instance


@pytest.fixture(scope="session")
def client(mock_settings):
    """TestClient with all external services mocked."""
    with patch("app.config.settings", mock_settings), \
         patch("app.services.github_service.gh", MagicMock()), \
         patch("app.services.gmail_service.build", MagicMock(), create=True), \
         patch("anthropic.Anthropic", MagicMock()):
        from main import app
        with TestClient(app) as c:
            yield c
