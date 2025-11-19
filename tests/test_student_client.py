"""Tests for StudentClient."""

from unittest.mock import Mock, patch

import pytest

from pyclasscharts.exceptions import AuthenticationError, ValidationError
from pyclasscharts.student_client import StudentClient


class TestStudentClient:
    """Test cases for StudentClient."""

    def test_throws_when_no_student_code_provided(self):
        """Test that login raises ValidationError when no student code is provided."""
        client = StudentClient("")
        with pytest.raises(ValidationError, match="Student Code not provided"):
            client.login()

    @patch("pyclasscharts.student_client.requests.post")
    def test_throws_with_invalid_student_code(self, mock_post):
        """Test that login raises AuthenticationError with invalid student code."""
        # Mock a response that doesn't have set-cookie header (failed auth)
        mock_response = Mock()
        mock_response.status_code = 200  # Not a redirect
        mock_response.headers = {}  # No set-cookie header
        mock_post.return_value = mock_response

        client = StudentClient("invalid")
        with pytest.raises(
            AuthenticationError,
            match="Unauthenticated: ClassCharts didn't return authentication cookies",
        ):
            client.login()

    @patch("pyclasscharts.student_client.requests.post")
    def test_throws_when_no_set_cookie_header(self, mock_post):
        """Test that login raises AuthenticationError when no set-cookie header."""
        mock_response = Mock()
        mock_response.status_code = 302  # Redirect
        mock_response.headers = {}  # No set-cookie header
        mock_post.return_value = mock_response

        client = StudentClient("code", "01/01/2000")
        with pytest.raises(
            AuthenticationError,
            match="Unauthenticated: ClassCharts didn't return authentication cookies",
        ):
            client.login()

    @patch("pyclasscharts.student_client.requests.post")
    @patch("pyclasscharts.student_client.StudentClient.get_new_session_id")
    @patch("pyclasscharts.student_client.StudentClient.get_student_info")
    @patch("pyclasscharts.student_client.parse_cookies")
    def test_login_success(
        self,
        mock_parse_cookies,
        mock_get_student_info,
        mock_get_new_session_id,
        mock_post,
    ):
        """Test successful login flow."""
        import json

        # Mock successful login response
        mock_response = Mock()
        mock_response.status_code = 302
        mock_response.headers = {
            "set-cookie": "student_session_credentials="
            + json.dumps({"session_id": "test_session_id"})
        }
        mock_post.return_value = mock_response

        # Mock cookie parsing
        mock_parse_cookies.return_value = {
            "student_session_credentials": json.dumps({"session_id": "test_session_id"})
        }

        # Mock get_new_session_id (no-op)
        mock_get_new_session_id.return_value = None

        # Mock get_student_info
        mock_get_student_info.return_value = {
            "data": {"user": {"id": 456, "name": "Test Student"}},
            "meta": {},
            "success": 1,
        }

        client = StudentClient("ABC123", "01/01/2000")
        client.login()

        assert client.session_id == "test_session_id"
        assert client.student_id == 456

    @patch("pyclasscharts.student_client.requests.post")
    @patch("pyclasscharts.student_client.StudentClient.get_new_session_id")
    @patch("pyclasscharts.student_client.StudentClient.get_student_info")
    @patch("pyclasscharts.student_client.parse_cookies")
    def test_student_code_uppercase(
        self,
        mock_parse_cookies,
        mock_get_student_info,
        mock_get_new_session_id,
        mock_post,
    ):
        """Test that student code is converted to uppercase during login."""
        import json

        client = StudentClient("abc123", "01/01/2000")
        assert client.student_code == "abc123"  # Stored as provided

        # Mock successful login response
        mock_response = Mock()
        mock_response.status_code = 302
        mock_response.headers = {
            "set-cookie": "student_session_credentials="
            + json.dumps({"session_id": "test_session_id"})
        }
        mock_post.return_value = mock_response

        # Mock cookie parsing
        mock_parse_cookies.return_value = {
            "student_session_credentials": json.dumps({"session_id": "test_session_id"})
        }

        # Mock get_new_session_id (no-op)
        mock_get_new_session_id.return_value = None

        # Mock get_student_info
        mock_get_student_info.return_value = {
            "data": {"user": {"id": 1}},
            "meta": {},
            "success": 1,
        }

        client.login()

        # Verify the code was sent in uppercase
        call_args = mock_post.call_args
        assert call_args is not None
        form_data = call_args.kwargs.get("data", {})
        assert form_data.get("code") == "ABC123"
