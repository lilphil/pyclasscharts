"""Tests for ParentClient."""

from unittest.mock import Mock, patch

import pytest

from pyclasscharts.exceptions import AuthenticationError, ValidationError
from pyclasscharts.parent_client import ParentClient


class TestParentClient:
    """Test cases for ParentClient."""

    def test_throws_when_no_email_provided(self):
        """Test that login raises ValidationError when no email is provided."""
        client = ParentClient("", "password")
        with pytest.raises(ValidationError, match="Email not provided"):
            client.login()

    def test_throws_when_no_password_provided(self):
        """Test that login raises ValidationError when no password is provided."""
        client = ParentClient("email", "")
        with pytest.raises(ValidationError, match="Password not provided"):
            client.login()

    @patch("pyclasscharts.parent_client.requests.post")
    def test_throws_with_invalid_username_and_password(self, mock_post):
        """Test that login raises AuthenticationError with invalid credentials."""
        # Mock a response that doesn't have set-cookie header (failed auth)
        mock_response = Mock()
        mock_response.status_code = 200  # Not a redirect
        mock_response.headers = {}  # No set-cookie header
        mock_post.return_value = mock_response

        client = ParentClient("invalid", "invalid")
        with pytest.raises(
            AuthenticationError,
            match="Unauthenticated: ClassCharts didn't return authentication cookies",
        ):
            client.login()

    @patch("pyclasscharts.parent_client.requests.post")
    def test_throws_when_no_set_cookie_header(self, mock_post):
        """Test that login raises AuthenticationError when no set-cookie header."""
        mock_response = Mock()
        mock_response.status_code = 302  # Redirect
        mock_response.headers = {}  # No set-cookie header
        mock_post.return_value = mock_response

        client = ParentClient("email", "password")
        with pytest.raises(
            AuthenticationError,
            match="Unauthenticated: ClassCharts didn't return authentication cookies",
        ):
            client.login()

    @patch("pyclasscharts.parent_client.requests.post")
    @patch("pyclasscharts.parent_client.ParentClient.get_pupils")
    @patch("pyclasscharts.parent_client.parse_cookies")
    def test_login_success(self, mock_parse_cookies, mock_get_pupils, mock_post):
        """Test successful login flow."""
        import json

        # Mock successful login response
        mock_response = Mock()
        mock_response.status_code = 302
        mock_response.headers = {
            "set-cookie": "parent_session_credentials="
            + json.dumps({"session_id": "test_session_id"})
        }
        mock_post.return_value = mock_response

        # Mock cookie parsing
        mock_parse_cookies.return_value = {
            "parent_session_credentials": json.dumps({"session_id": "test_session_id"})
        }

        # Mock get_pupils to return a pupil
        mock_get_pupils.return_value = [{"id": 123, "name": "Test Pupil"}]

        client = ParentClient("email@example.com", "password")
        client.login()

        assert client.session_id == "test_session_id"
        assert client.student_id == 123

    def test_select_pupil_success(self):
        """Test selecting a pupil by ID."""
        client = ParentClient("email", "password")
        client.pupils = [
            {"id": 1, "name": "Pupil 1"},
            {"id": 2, "name": "Pupil 2"},
        ]
        client.student_id = 1

        client.select_pupil(2)
        assert client.student_id == 2

    def test_select_pupil_not_found(self):
        """Test that selecting a non-existent pupil raises ValidationError."""
        client = ParentClient("email", "password")
        client.pupils = [{"id": 1, "name": "Pupil 1"}]

        with pytest.raises(ValidationError, match="No pupil with specified ID found"):
            client.select_pupil(999)

    def test_select_pupil_no_id(self):
        """Test that selecting with no ID raises ValidationError."""
        client = ParentClient("email", "password")
        client.pupils = [{"id": 1, "name": "Pupil 1"}]

        with pytest.raises(ValidationError, match="No pupil ID specified"):
            client.select_pupil(0)
