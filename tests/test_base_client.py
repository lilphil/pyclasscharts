"""Tests for BaseClient."""

import time
from unittest.mock import Mock, patch

import pytest

from pyclasscharts.base_client import BaseClient
from pyclasscharts.exceptions import APIError, NoSessionError


class ConcreteBaseClient(BaseClient):
    """Concrete implementation of BaseClient for testing."""

    def __init__(self, api_base: str = "https://test.api"):
        super().__init__(api_base)

    def login(self):
        """Mock login implementation."""
        self.session_id = "test_session"
        self.last_ping = time.time() * 1000


class TestBaseClient:
    """Test cases for BaseClient."""

    def test_no_session_id_raises_error(self):
        """Test that making a request without a session ID raises NoSessionError."""
        client = ConcreteBaseClient()
        # Don't call login, so session_id is empty

        with pytest.raises(NoSessionError, match="No session ID"):
            client._make_authed_request("https://test.api/endpoint")

    def test_api_error_on_failed_response(self):
        """Test that API errors are raised when success is 0."""
        client = ConcreteBaseClient()
        client.login()

        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "success": 0,
                "error": "Test error message",
                "data": {},
                "meta": {},
            }
            mock_response.text = '{"success": 0, "error": "Test error message"}'
            mock_request.return_value = mock_response

            with pytest.raises(APIError, match="Test error message"):
                client._make_authed_request("https://test.api/endpoint")

    def test_json_decode_error(self):
        """Test that JSON decode errors are handled properly."""
        import json

        client = ConcreteBaseClient()
        client.login()

        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "Not JSON", 0)
            mock_response.text = "Not JSON"
            mock_request.return_value = mock_response

            with pytest.raises(APIError, match="Error parsing JSON"):
                client._make_authed_request("https://test.api/endpoint")

    def test_session_revalidation(self):
        """Test that session ID is revalidated when it's old."""
        client = ConcreteBaseClient()
        client.login()
        # Set last_ping to be old (more than 3 minutes ago)
        client.last_ping = time.time() * 1000 - 200000  # ~3.3 minutes ago

        with patch.object(client, "get_new_session_id") as mock_revalidate:
            with patch.object(client._session, "request") as mock_request:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "success": 1,
                    "data": {},
                    "meta": {},
                }
                mock_request.return_value = mock_response

                client._make_authed_request("https://test.api/endpoint")

                # Should have called get_new_session_id
                mock_revalidate.assert_called_once()

    def test_get_new_session_id(self):
        """Test that get_new_session_id updates session ID."""
        client = ConcreteBaseClient()
        client.login()

        with patch.object(client, "_make_authed_request") as mock_request:
            mock_request.return_value = {
                "meta": {"session_id": "new_session_id"},
                "data": {},
                "success": 1,
            }

            client.get_new_session_id()

            assert client.session_id == "new_session_id"
            assert client.last_ping > 0
