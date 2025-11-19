"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def mock_requests(monkeypatch):
    """Fixture to mock requests library."""
    from unittest.mock import Mock

    import requests

    class MockResponse:
        def __init__(self, status_code=200, headers=None, json_data=None, text=""):
            self.status_code = status_code
            self.headers = headers or {}
            self._json_data = json_data
            self.text = text

        def json(self):
            return self._json_data or {}

    mock_post = Mock()
    mock_get = Mock()
    mock_request = Mock()

    def mock_post_func(*args, **kwargs):
        return MockResponse()

    def mock_get_func(*args, **kwargs):
        return MockResponse()

    def mock_request_func(self, *args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "post", mock_post_func)
    monkeypatch.setattr(requests, "get", mock_get_func)
    monkeypatch.setattr(requests.Session, "request", mock_request_func)

    return {
        "post": mock_post,
        "get": mock_get,
        "request": mock_request,
    }
